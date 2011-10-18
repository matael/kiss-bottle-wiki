#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import sys
import os
import codecs
from markdown import markdown
from bottle import\
        Bottle,\
        run,\
        route,\
        template,\
        static_file,\
        error,\
        debug

# Uncomment to run in a WSGI server
#os.chdir(os.path.dirname(__file__))

application = Bottle()
debug(True)

@application.route('/static/:filename')
def server_static(filename):
    """ Serve Static files """
    return static_file(filename, root='static/')

@application.error(404)
def mistake404(code):
    """ 404 Error """
    return template('templates/404.html')
def _compile_page(name):
    if name=='' or name=='None':
        name='index'
    filename = "src/{0}.mkd".format(name)
    file = codecs.open(filename, 'r', encoding='utf8')
    text = markdown(file.read())
    template = open("templates/page.html",'r')
    return str(template.read()).format(text)

@application.route('/')
@application.route('/page')
@application.route('/page/:name')
def show_page(name=''):
    return _compile_page(name)

def main():
    run(application, host='localhost', port=8080)
    return 0

if __name__ == '__main__': main()

