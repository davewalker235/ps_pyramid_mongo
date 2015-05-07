import pymongo
import gridfs
from ps import contexts
from ps import renderers
from ps import models
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator

def main(global_config, **settings):
  """ This function returns a Pyramid WSGI application.
      Should also launch spawn process for compilers or Gulp:
        stylus -w -m -u nib -u jeet -o ../static --include-css
        coffee -w
  """

  def roles(userid, req):
    if req.user:
      roles = ['role:'+role for role in req.user.role]
      roles.append(req.user._id)
      return roles if roles else []
    else:
      return None

  def user(req):
    """ This returns a user object from Mongo, a SON Manipulator automatically coverts items from
        the users collection into User() objects.  The lookup is done with req.unauthenticated_userid,
        because authenticated_userid relies on the roles() callback, which creates a loop because
        the roles() function uses req.user.  Unauthenticated_userid is just a pointer to the raw _id
    """
    if req.unauthenticated_userid:
      user = req.db.user.find_one({'_id': ObjectId(req.unauthenticated_userid)})
      user.req = req
      return user
    else:
      return None

  def flash(req, msg, status="success"):
    message = '<div class="msg {}">{}</div>'.format(status, msg)
    req.session.flash(message)

  settings.setdefault('env', 'dev')

  config = Configurator(default_permission='view', settings=settings, root_factory=contexts.Root)
  config.add_static_view('static', 'static', cache_max_age=3600)
  config.scan()

  # Authorization and Security Measures
  # Should change the authentication key for production
  config.set_authorization_policy(ACLAuthorizationPolicy())
  config.set_authentication_policy(AuthTktAuthenticationPolicy('Flyj7PsggCNq4UF5xRTLbwltZFnV0L6',
    hashalg='sha512', callback=roles, reissue_time=360, timeout=1800))

  # Add database connections and SON Manipulator for automatic conversions
  # Just using basic IP restrictions for mongo security, let pymongo handle connection performance
  mongo = pymongo.Connection().ps
  mongo.add_son_manipulator(models.Transform())
  mongofs = gridfs.GridFS(mongo)

  # Add database and helper methods to request object
  config.add_request_method(lambda req: mongo, 'db', reify=True)
  config.add_request_method(lambda req: mongofs, 'fs', reify=True)
  config.add_request_method(user, 'user', reify=True)
  config.add_request_method(flash, 'flash')

  # Add renderers, ajax renderer is standardized to send flash messages and errors
  config.add_renderer('.mustache', renderers.Mustache)
  config.add_renderer('ajax', renderers.Ajax)

  return config.make_wsgi_app()