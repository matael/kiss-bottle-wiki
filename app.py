#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import sys
import os
import codecs
import re
from markdown import markdown
from bottle import\
        Bottle,\
        run,\
        route,\
        template,\
        static_file,\
        error,\
        debug,\
        request,\
        redirect

# Uncomment to run in a WSGI server
#os.chdir(os.path.dirname(__file__))

application = Bottle()
debug(True)
    
# WIKI_RE
WIKI_RE = re.compile('\[\[([^\]]*)\]\]')

@application.route('/static/:filename')
def server_static(filename):
    """ Serve Static files """
    return static_file(filename, root='static/')

@application.error(404)
def mistake404(code):
    """ 404 Error """
    return template('templates/404.html')


@application.error(500)
def mistake500(code):
    """ 500 Error """
    return template('templates/500.html')


def _compile_page(filename):
    file = codecs.open(filename, 'r', encoding='utf8')
    text = WIKI_RE.sub(r'[\1](\1)',file.read())
    print(text)
    text = markdown(text)
    template = open("templates/page.html",'r')
    return str(template.read()).format(text)


@application.route('/')
@application.route('/:name')
def show_page(name=''):
    return _compile_page(name)

def main():
    run(application, host='0.0.0.0', port=8080)
    return 0

if __name__ == '__main__': main()

