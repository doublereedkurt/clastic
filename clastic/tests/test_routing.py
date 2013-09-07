from __future__ import unicode_literals
from nose.tools import raises, eq_, ok_
from json import loads

from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse

from clastic import Application, render_basic
from clastic import GET, POST, PUT, DELETE


def api(api_path):
    return 'api: %s' % api_path


def two_segments(one, two):
    return 'two_segments: %s, %s' % (one, two)


def three_segments(one, two, three):
    return 'three_segments: %s, %s, %s' % (one, two, three)


def test_create_route_order_list():
    "tests route order when routes are added as a list"
    routes = [('/api/<path:api_path>', api, render_basic),
              ('/<one>/<two>', two_segments, render_basic),
              ('/<one>/<two>/<three>', three_segments, render_basic)]
    app = Application(routes)
    client = Client(app, BaseResponse)
    yield eq_, client.get('/api/a').data, 'api: a'
    yield eq_, client.get('/api/a/b').data, 'api: a/b'

    for i, rule in enumerate(app.wmap._rules):
        yield eq_, rule.rule, routes[i][0]
    return


def test_create_route_order_incr():
    "tests route order when routes are added incrementally"
    routes = [('/api/<path:api_path>', api, render_basic),
              ('/<one>/<two>', two_segments, render_basic),
              ('/<one>/<two>/<three>', three_segments, render_basic)]
    app = Application()
    client = Client(app, BaseResponse)
    for r in routes:
        app.add(r)
        yield eq_, client.get('/api/a/b').data, 'api: a/b'
        yield eq_, app.wmap._rules[-1].rule, r[0]
    return


def test_http_methods_success():
    "tests route order when routes are added incrementally"
    ep = lambda _route: repr(_route.methods)
    routes = [GET('/', ep, render_basic),
              POST('/', ep, render_basic),
              PUT('/', ep, render_basic),
              DELETE('/', ep, render_basic)]
    app = Application(routes)
    client = Client(app, BaseResponse)
    methods = ('get', 'post', 'put', 'delete')
    for method in methods:
        req_func = getattr(client, method)
        resp_data = req_func('/').data
        # lololol yay eval()
        route_methods = eval(resp_data) - set(['HEAD'])
        yield eq_, set([method.upper()]), route_methods
    return
