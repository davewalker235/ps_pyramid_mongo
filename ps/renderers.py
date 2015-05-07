import pystache
import json

class Ajax:
  def __init__(self, info):
    self.info = info

  def __call__(self, value, system):
    # Trigger some action if the request 403s or does not return, separate out flash messages
    # for display
    request = system.get('request')
    request.response.content_type = 'application/json'
    value['flash'] =  ''.join(request.session.pop_flash())
    return json.dumps(value)


class Mustache:
  # Save templates in cache as requested in the live version
  # Use re.sub("\n\s*", "", template) to compress whitespace, you'll need to handle partials
  # with some sort of custom loader for these {{> partial}}

  _cache = {}

  def __init__(self, info):
    self.info = info

  def __call__(self, value, system):
    print(__file__)
    self.renderer = pystache.Renderer(search_dirs='/home/dave/Web/partyspace/python/ps2/ps/ps/templates')
    req = system['request']

    with open('ps/templates/'+self.info.name) as f:
      template_stream = f.read()

    with open('ps/templates/layout/base.mustache') as f:
      layout_stream = f.read().replace('{{> body}}', template_stream)

    # Add some default values back in for mustache
    value.update(system)
    value['flash'] = ''.join(system['request'].session.pop_flash())
    value['POST'] = req.POST.mixed()
    value['site'] = {
      'name' : 'Partyspace',
      'url' : 'http://partyspace.com',
    }

    return self.renderer.render(layout_stream, value)