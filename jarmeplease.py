#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import sys, os
from subprocess import check_output as run

BASE = os.getcwd()
EXT = os.path.join(BASE, 'ext')
EXTLIB = os.path.join(BASE, 'ext-lib')

commands = dict()

def command(f):
    name = f.func_name
    commands[name] = f
    return f

def assert_dir_exists(path):
    '''checks if a directory exists. if not it creates it. if something exists
    and it is not a directory it raises an runtime error
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        os.mkdir(path)
    elif not os.path.isdir(path):
        msg = 'Expected a directory found a file. "%(path)s"' % locals()
        raise RuntimeError, msg
    return path

def check_file_exists(path):
    '''checks if a file exists.
    @returns boolean
    '''
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return False
    elif not os.path.isfile(path):
        return False
    return True

def chain(arg, *args):
    cmds = ' && '.join([arg] + list(args))
    print cmds
    return run(['bash', '-c', cmds])

def checked_out(lib, conf):
    url = conf.url
    src_dir = os.path.join(EXT, lib)
    print chain(
      'cd '+EXT,
      'if [ ! -d %(lib)s ] ; then git clone %(url)s %(lib)s; fi' % locals()
    )
    chain(
      'cd '+src_dir,
      'git checkout '+conf.branch
    )

def update(lib, conf):
    src_dir = os.path.join(EXT, lib)
    git_dir = os.path.join(src_dir, '.git')
    local = conf.branch
    remote = 'origin/' + conf.branch
    chain('git --git-dir=%(git_dir)s remote update' % locals())
    tags = chain('cd '+src_dir, 'git tag').split('\n')
    print tags
    chain('cd '+src_dir, 'git checkout '+conf.branch)
    if conf.branch not in tags:
        lmsg = chain(
        'git --git-dir=%(git_dir)s show-branch --sha1-name %(local)s' % locals())
        rmsg = chain(
        'git --git-dir=%(git_dir)s show-branch --sha1-name %(remote)s' % locals())
        if lmsg != rmsg:
            chain('cd '+src_dir, 'git pull origin %(local)s' % locals())
            build(lib, conf)
    if not check_file_exists(os.path.join(EXT, conf['jar-location'])):
        build(lib, conf)

def build(lib, conf):
    src_dir = os.path.join(EXT, lib)
    chain(
      'cd '+src_dir,
      'git checkout '+conf.branch
    )
    chain('cd '+src_dir, conf['build-command'])

def install(lib, conf):
    src = os.path.join(EXT, conf['jar-location'])
    dest = os.path.join(EXTLIB, conf['final-name'])
    chain('cp %(src)s %(dest)s' % locals())

def jar(lib, conf):
    checked_out(lib, conf)
    update(lib, conf)
    install(lib, conf)

@command
def jarall(conf):
    for lib, c in conf.iteritems(): jar(lib, c)

@command
def nuke(conf):
    chain('rm -rf ' + EXT)
    chain('rm -rf ' + EXTLIB)

@command
def clean(conf):
    el = EXTLIB
    try: chain('rm %(el)s/*.jar' % locals())
    except: pass
    for lib, libconf in conf.iteritems():
        src_dir = os.path.join(EXT, lib)
        chain('cd '+src_dir, libconf['clean-command'])

assert_dir_exists(EXT)
assert_dir_exists(EXTLIB)

