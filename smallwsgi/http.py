# -*- coding: utf-8 -*-

import json
from webob import Request,Response

def jresponse(status,msg,req,status_int,headers=None,statusstr='',param=None):
    
    msg = msg.lower()
    data = {'status':str(status),'msg':str(msg)}
    
    if param:
        data.update(param)
        
    container_list = json.dumps(data)
    if headers:
        ret = Response(body=container_list, request=req,headers=headers)
    else:
        ret = Response(body=container_list, request=req)
        
    ret.content_type = 'application/json'
    ret.charset = 'utf-8'
    ret.status_int = status_int
    if statusstr:
        ret.status = statusstr
        
    if status != '0' and req.method == 'PUT': 
        pass

    return ret
