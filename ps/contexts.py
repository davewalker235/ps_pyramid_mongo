from pyramid.security import (
  Allow,
  Authenticated,
  Deny,
  Everyone,
  ALL_PERMISSIONS,
  DENY_ALL,
  )

class Root:
  __name__ = ''
  __parent__ = None
  __acl__ = [(Allow, Everyone, 'view'), DENY_ALL]

  def __init__(self, req):
    self.req = req

  def __getitem__(self, key):
    keys = {
      'user': UserDispatch,
      'users': Users,
      'register': Register,
    }

    if keys.get(key): return keys[key](self)
    print(key)
    raise KeyError



class Users:
  __name__ = 'users'
  __acl__ = [(Allow, 'group:admin', ALL_PERMISSIONS), DENY_ALL]

  def __init__(self, parent):
    self.__parent__ = parent
    self.req = parent.req



class UserDispatch:
  __name__ = 'user'
  __acl__ = [
      (Allow, 'group:admin', ALL_PERMISSIONS),
      (Allow, Everyone, ['register', 'login']),
      DENY_ALL
      ]

  def __init__(self, parent):
    self.__parent__ = parent
    self.req = parent.req

  def __getitem__(self, key):
    raise KeyError



class User:
  __name__ = None
  def __acl__(self):
    return [
      (Allow, self.owner, 'view')
    ]



class Register:
  __name__ = 'register'
  __acl__ = [(Allow, Everyone, ALL_PERMISSIONS)]

  def __init__(self, parent):
    self.__parent__ = parent
    self.req = parent.req

  def __getitem__(self, key):
    raise KeyError