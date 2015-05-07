from passlib.hash import sha512_crypt
from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from ps import contexts
from ps.forms import registration
from ps import models
import pystache
import copy


@view_defaults(context=contexts.Register)
class Register:
  def __init__(self, req):
    self.req = req
    self.form = registration.Form(req)

  def make_user(self, _type = 'personal'):
    req = self.req

    if self.form.validated:
      post = req.POST
      data = {
        'name': post['name'],
        'email': post['email'],
        'password': sha512_crypt.encrypt(post['password']),
        'type': [_type],
      }
      user = models.User(req, data)
      try:
        user.activate()
        return HTTPFound('/login')
      except ValueError as e:
        req.flash(e, 'error')

    return self.form

  @view_config(renderer='register/personal.mustache')
  def personal(self):
    form = self.make_user()
    return {'form': form}

  @view_config(renderer='register/corporate.mustache', name='corporate')
  def corporate(self):
    form = self.make_user('corporate')
    return {'form': form}
