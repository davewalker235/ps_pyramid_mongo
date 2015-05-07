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
      Should also launch compilers or Gulp:
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
    # authenticated_userid only returns if the roles callback is != None, unauthenticated_userid
    # is just a pointer to the raw session user id
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
  config.set_authorization_policy(ACLAuthorizationPolicy())
  config.set_authentication_policy(AuthTktAuthenticationPolicy('Flyj7PsggCNq4UF5xRTLbwltZFnV0L6',
    hashalg='sha512', callback=roles, reissue_time=360, timeout=1800))

  # Add database connections
  mongo = pymongo.Connection().ps
  mongo.add_son_manipulator(models.Transform())
  mongofs = gridfs.GridFS(mongo)

  config.add_request_method(lambda req: mongo, 'db', reify=True)
  config.add_request_method(lambda req: mongofs, 'fs', reify=True)
  config.add_request_method(user, 'user', reify=True)
  config.add_request_method(flash, 'flash')

  # Add renderers
  config.add_renderer('.mustache', renderers.Mustache)
  config.add_renderer('ajax', renderers.Ajax)

  return config.make_wsgi_app()