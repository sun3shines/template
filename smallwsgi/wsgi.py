# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8" )

import errno
import os
import signal
import time
import mimetools
from itertools import chain
from StringIO import StringIO
import syslog

import eventlet
from eventlet import greenio, GreenPool, sleep, wsgi, listen
from paste.deploy import loadapp, appconfig
from eventlet.green import socket, ssl
from webob import Request
from urllib import unquote
import syslog

def monkey_patch_mimetools():
    
    orig_parsetype = mimetools.Message.parsetype

    def parsetype(self):
        if not self.typeheader:
            self.type = None
            self.maintype = None
            self.subtype = None
            self.plisttext = ''
        else:
            orig_parsetype(self)

    mimetools.Message.parsetype = parsetype


def get_socket(bind_ip='0.0.0.0',default_port=8080,backlog=4096,cert_file=None,key_file=None):
    
    bind_addr = (bind_ip,default_port)
    
    address_family = [addr[0] for addr in socket.getaddrinfo(bind_addr[0],
            bind_addr[1], socket.AF_UNSPEC, socket.SOCK_STREAM)
            if addr[0] in (socket.AF_INET, socket.AF_INET6)][0]
    sock = None
    retry_until = time.time() + 30
    
    while not sock and time.time() < retry_until:
        try:
            sock = listen(bind_addr, backlog=int(backlog),
                        family=address_family)
            
        except socket.error, err:
            if err.args[0] != errno.EADDRINUSE:
                raise
            sleep(0.1)
    if not sock:
        raise Exception('Could not bind to %s:%s after trying for 30 seconds' %
                        bind_addr)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 600)
    
    return sock


def run_wsgi(conf_file, app_section,bind_ip='0.0.0.0',default_port=8080):
    
    log_name = app_section
    
    sock = get_socket(bind_ip,default_port)
        
    loadapp('config:%s' % conf_file, global_conf={'log_name': log_name})

    def run_server():
        wsgi.HttpProtocol.default_request_version = "HTTP/1.0"
        
        wsgi.WRITE_TIMEOUT =  60
        eventlet.hubs.use_hub('poll')
        eventlet.patcher.monkey_patch(all=False, socket=True)
        monkey_patch_mimetools()
        app = loadapp('config:%s' % conf_file,
                      global_conf={'log_name': log_name})
        pool = GreenPool(size=100)
        try:
            wsgi.server(sock, app, log=None, custom_pool=pool)
        except socket.error, err:
            if err[0] != errno.EINVAL:
                raise
        pool.waitall()

    run_server()
    
    greenio.shutdown_safe(sock)
    sock.close()
    syslog.syslog(syslog.LOG_ERR,'Exited')


