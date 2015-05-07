import unittest
from pyramid import testing

# TODO: Really gotta step up your game on these tests, the selenium stuff won't cut it

class AppTests(unittest.TestCase):
  def test_main(self):
    from . import main
    print(main(''))

  def test_user(self):
    request = testing.DummyRequest()
    print(request.user)


class ViewTests(unittest.TestCase):
  def setUp(self):
    self.config = testing.setUp()

  def tearDown(self):
    testing.tearDown()

  def test_home(self):
    from .views import home
    req = testing.DummyRequest()
    info = home(req)
    self.assertEqual(info['project'], 'ps')

  def test_register(self):
    from .views import Register
    req = testing.DummyRequest()
    info = Register.personal(req)
    self.assertEqual(info['error'], True)

class ContextTests(unittest.TestCase):
  def test_root(self):
    from .contexts import Root
    root = Root(testing.DummyRequest())
    with self.assertRaises(KeyError):
      root['test']
