#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import sys
import os
import codecs
import re
from markdown import markdown
import git
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

#####################################
############  SETTINGS  #############
#####################################

# remember to use trailling slash
ROOT_PATH = "/absolute/path/to/kbw/"

#####################################
#####################################

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


def _compile_page(filename,name):
    file = codecs.open(filename, 'r', encoding='utf8')
    text = WIKI_RE.sub(r'[\1](\1)',file.read())
    text = markdown(text)
    template = codecs.open("templates/page.html",'r', encoding='utf8')
    return unicode(template.read()).format(text,name)

def _commit_page(name, resume_line):
    try:
        index = git.Repo(ROOT_PATH).index
        index.add(["src/{0}.mkd".format(name)])
        index.commit(resume_line)
    except:
        pass


@application.route('/edit')
@application.route('/:name/edit')
@application.route('/edit', method="POST")
@application.route('/:name/edit', method="POST")
def edit_page(name=''):
    if name=='' or name==None:
        name = 'index'
    if request.method == "GET":
        try:
            file = open('src/{0}.mkd'.format(name))
        except IOError:
            if os.path.exists('src/{0}.mkd.save'.format(name)):
                return template('templates/comelater.html', name=name)  
            else:
                return template('templates/editpage.html', name=name, content='')
        text = file.read()
        file.close()
        os.remove('src/{0}.mkd'.format(name))
        save = open('src/{0}.mkd.save'.format(name),'w')
        save.write(text)
        save.close()
        return template('templates/editpage.html', name=name, content=text)
    elif request.method == "POST":
        content = request.POST['content']
        if request.POST['resume_line'] != '':
            resume_line = request.POST['resume_line']
        else:
            resume_line = 'update page'
        file = open('src/{0}.mkd'.format(name),'w')
        file.write(content)
        file.close()
        _commit_page(name, resume_line)
        try:
            os.remove('src/{0}.mkd.save'.format(name))
        except : pass
        return redirect("/{0}".format(name))


@application.route('/')
@application.route('/:name')
def show_page(name=''):
    if name=='' or name=='None':
        name='index'
    filename = "src/{0}.mkd".format(name)
    if not os.path.exists(filename):
        filename = '{0}.save'.format(filename)
    if not os.path.exists(filename):
        return redirect("/{0}/edit".format(name))
    return _compile_page(filename,name)


def main():
    run(application, host='0.0.0.0', port=8080)
    return 0

if __name__ == '__main__': main()

