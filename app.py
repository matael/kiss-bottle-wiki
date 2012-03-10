#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import sys
import os
import codecs
import re
import datetime
import time
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
METADATA = ';;;- '
METADATA_RE = re.compile(";;;- ")

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
    text = ""
    cur = file.readline()
    while cur:
        if not METADATA_RE.search(cur):
            text+=cur # crappy concatenation
        cur = file.readline()
    text = WIKI_RE.sub(r'[\1](\1)',text)
    text = markdown(text, ['extra'])
    template = codecs.open("templates/page.html",'r', encoding='utf8')
    return unicode(template.read()).format(text,name)

def _commit_page(name, resume_line):
    repo = git.Repo(ROOT_PATH).git
    repo.add("src/{0}.mkd".format(name))
    repo.commit(m=resume_line)


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
                f = open('src/{0}.mkd.save'.format(name))
                f.seek(-17,2)
                old_ts = int(f.read().lstrip(METADATA).rstrip())
                if (old_ts-int(time.mktime(datetime.datetime.now().timetuple()))) < 1800:
                    f.close()
                    file = open('src/{0}.mkd.save'.format(name))
                    pass
                else:
                    return template('templates/comelater.html', name=name)  
            else:
                return template('templates/editpage.html', name=name, content='')
        # Get current content
        text = ""
        cur = file.readline()
        while cur:
            if not METADATA_RE.search(cur):
                text+=cur # crappy concatenation
            cur = file.readline()
        file.close()
        # Create backup file
        try:
            os.remove('src/{0}.mkd'.format(name))
        except OSError:
            pass
        save = open('src/{0}.mkd.save'.format(name),'w')
        save.write(text) # current content
        # security string
        save.write("\n{0} {1}\n".format(METADATA, int(time.mktime(datetime.datetime.now().timetuple()))))
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


@application.route('/upload')
@application.route('/upload', method="POST")
def upload():
    """ View handling file uploads """
    if request.method=="GET":
        return template('templates/upload_form.html')
    elif request.method=="POST":
        data = request.files['data']
        current_articles = [_.rstrip('.save').rstrip('.mkd') for _ in os.listdir('src/')]
        if data.filename in current_articles:
            return redirect("/{0}".format(data.filename))
        dest_file = open("src/{0}.mkd".format(data.filename), 'w')
        dest_file.write(data.file.read())
        dest_file.close()
        return redirect("/{0}".format(data.filename))


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

