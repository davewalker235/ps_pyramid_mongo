import re
import pystache

class Form:
  """ This is a basic form class, intended for scaffolding out forms and inputs with reasonable
      validation and error message baked in.  Other form libraries didn't play well with mustache.
      Should separate these into base classes and extend new forms from there.
  """
  def __init__(self, req):
    self.req = req
    self.validated = False
    self.errors = set()
    self.classes = Classes()

    self.name = Name(self, 'name', required=True)
    self.email = Email(self, 'email', required=True)
    self.password = Password(self, 'password', 'password')
    self.confirm_password = ConfirmPassword(self, 'confirm_password', 'password')

    if req.POST: self.validate()

  def add_error(self, msg):
    self.validated = False
    self.classes.add('has-errors')
    self.errors.add(msg)

  def validate(self):
    self.validated = True
    post = self.req.POST

    # Clean data before validation
    # Strip extra whitespace, leave in for password so it will generate an error message
    post.email = post['email'].strip()
    post.name = post['name'].strip()

    self.email.validate()
    self.name.validate()
    self.password.validate()

    return self.validated


class Input:
  def __init__(self, form, name, input_type = 'text', **kwargs):
    for key, value in kwargs.items(): setattr(self, key, value)
    self.form = form
    self.req = form.req
    self.name = name
    self.type = input_type
    self.classes = Classes()
    self.errors = Errors()
    self.required = getattr(self, 'required', False)
    if self.required: self.classes.add('required')
    if not getattr(self, 'label', None): self.label = self.name.replace('_', ' ').title()
    if self.req.POST:
      self.value = form.req.POST.get(self.name)

  def __str__(self):
    template = """
      <div class="{{classes}}">
        <div>
        <label for="{{name}}">{{label}}</label>
        <input type="{{type}}" name="{{name}}" id="{{name}}" value="{{value}}">
        </div>
        {{{errors}}}
      </div>"""
    return pystache.render(template, self)

  def add_error(self, msg):
    self.classes.add('error')
    self.form.classes.add('error')
    self.form.validated = False
    self.errors.add(msg)



class Classes(set):
  def __str__(self):
    return ' '.join(self)



class Errors(set):
  def __str__(self):
    if self:
      template = '''<div class="error-list">{{#errors}}
          <div class="msg error">{{{.}}}</div>
        {{/errors}}</div>'''
      return pystache.render(template, {'errors': self})
    else:
      return ""


class Password(Input):
  def validate(self):
    form = self.form
    post = form.req.POST
    if post:
      password = post[self.name]
      if password:
        symbols = ['$','&','#','@','*', '~']
        re_symbols = [re.escape(symbol) for symbol in symbols]
        if len(password) < 8:
          self.add_error('Must be at least 8 characters long.')
        if not re.match('^[a-zA-Z0-9{0}]*$'.format(''.join(re_symbols)), password):
          self.add_error('''Can only contain letters, numbers, and
            these characters: '''+' '.join(symbols))
        if not re.search('[A-Z]', password) or not re.search('[0-9]', password):
          self.add_error('Must contain at least one uppercase letter and one number')
        if password != post['confirm_password']:
          self.form.confirm_password.add_error("Your password confirmation does not match your password.")
      else:
        self.add_error('You must provide a password')

  pass

class ConfirmPassword(Input):
  pass

class Email(Input):
  def validate(self):
    form = self.form
    post = form.req.POST
    post[self.name] = post[self.name].strip()
    if post:
      self.value = post[self.name]
      email = post[self.name]
      if email:
        first = email.find('@')
        second = email.rfind('.')
        if first >= second:
          self.add_error('Oops, looks like you may have mistyped your email address.')
        else:
          user = form.req.db.users.find_one({'email': email})
          if user:
            self.add_error('''Hmmm, this email address already has an account, have you
              <a href="/user/reset-password">forgotten your password</a>?''')
      else:
        self.add_error("We'll need your email address in case you need to reset your password!")

class Name(Input):
  def validate(self):
    post = self.form.req.POST
    name = post[self.name].strip().title()
    self.value = name
    if not name:
      self.add_error("We need your name, don't worry, we're friendly.")
