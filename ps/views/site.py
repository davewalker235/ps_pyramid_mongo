from passlib.hash import sha512_crypt
from pyramid.view import view_config
from ps import contexts

@view_config(context=contexts.Root, renderer='site/home.mustache')
def home(req):
  return {}


@view_config(context=contexts.Root, name='login', renderer='site/login.mustache')
def login(req):
  if req.POST:
    user = req.db.users.find_one({'email': req.POST['email']})
    if user:
      print(sha512_crypt.verify(req.POST['password'], user['password']))
    else:
      req.flash('Login failed, please try again or use the reset password feature.', 'error')
  return {}