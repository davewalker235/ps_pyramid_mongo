from .user import User
from pymongo.son_manipulator import SONManipulator

class Transform(SONManipulator):
  def transform_outgoing(self, son, collection):
    if collection.name == 'users':
      return User(son, collection)

    return son