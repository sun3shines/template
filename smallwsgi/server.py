# -*- coding: utf-8 -*-

from __future__ import with_statement

from eventlet import Timeout
from webob import Request, Response
from smallwsgi.route import process_request
    
class ServerController(object):

    def __init__(self, conf):
        pass
 
    def __call__(self, env, start_response):
        request = Request(env)
        
        try:
            resp = process_request(request) 
        except (Exception, Timeout):
            print 'ERROR __call__ error with %s %s ' % (request.method,request.path)
            resp = Response() 
                
        return resp(env, start_response)

def app_factory(global_conf, **local_conf):
    conf = global_conf.copy()
    conf.update(local_conf)
    return ServerController(conf)

