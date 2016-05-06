# -*- coding: utf-8 -*-

import smallwsgi.static
from smallwsgi.wsgi import run_wsgi

def start():

    print smallwsgi.static.PROC_HOST,smallwsgi.static.PROC_PORT
    
    run_wsgi(smallwsgi.static.PROC_PASTE_CONF, 
             smallwsgi.static.PROC_PASTE_APP_SECTION, 
             smallwsgi.static.PROC_HOST,
             smallwsgi.static.PROC_PORT)
    
if __name__ == '__main__':
    start()
    
