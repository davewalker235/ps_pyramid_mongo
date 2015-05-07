import uuid
import datetime

class User:
  def __init__(self, son, collection):
    self.son = son
    self.collection = collection

  @property
  def display_name(self):
    return self.son.get('name', self.son['email'])

  def save(self):
    email = self.son.get('email')
    if not email: raise KeyError('All users must have an email address')

    _id = self.son.get('_id')
    if not _id:
      user = self.collection.find_one({'email': email})
      if user: raise ValueError('This email address already has an account')

    _id = self.collection.save(self.son)
    self.son.setdefault('_id', _id)
    return _id

  def set_activation_code(self):
    self.son['activation_code'] = {
      'code': uuid.uuid4().hex,
      'expires': datetime.datetime.now() + datetime.timedelta(days = 7)
    }
    return self.save()