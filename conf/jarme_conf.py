#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, logging
import cStringIO as sio

from conf import BaseConfig
import log_conf
log = logging.getLogger('server_conf')

CONF_LOADED = False
conf = None

CUR_DIR = os.getcwd()
LOC_1 = os.path.join(CUR_DIR, 'Autobuild')
LOC_2 = os.path.join(CUR_DIR, 'autobuild')

def Type(f):
    def checker(*args):
        if len(args) > 1: raise RuntimeError, 'too many arguments'
        return f(*args)
    return checker

@Type
def Required(f):
    def checker(*args):
        if len(args) == 0: raise ValueError, 'option required'
        return f(*args)
    return checker

@Type
def scm(*args):
    if len(args) == 0: return None
    arg = args[0]
    if arg in ('git',): return arg
    else: raise ValueError, 'scm %s not yet supported' % arg

SCHEMA = {
    '__undefinedkeys__': {
        'scm': scm, # which scm?
        'url': Required(str), # where?
        'branch': Required(str),
        'jar-location': Required(str), # where will the jar be located?
        'final-name': Required(str), # what do you want the jar called?
        'build-command': Required(str), # how do we build?
        'clean-command': Required(str), # how do we clean?
    }
}

def get_conf(supplied_loc=None):
    global conf
    global CONF_LOADED
    if CONF_LOADED: return conf
    locs = [LOC_2, LOC_1, supplied_loc]
    valid_locs = [
        loc
        for loc in locs
        if loc is not None and os.path.exists(loc)
    ]
    if not valid_locs:
        raise RuntimeError, "No buildfiles found looked at: %s" % str(locs)
    conf = AutobuildConfig(SCHEMA, valid_locs[0])
    CONF_LOADED = True
    return conf

class AutobuildConfig(BaseConfig):
    '''
    The server configuration class. Allows for customized defaults checking if
    required.
    '''

    def __init__(self, *args, **kwargs):
        self.__check_defaults()
        super(AutobuildConfig, self).__init__(*args, **kwargs)

    def __check_defaults(self):
        '''
        Place defaults checks here, will get called after dict is loaded but
        before it gets exposed and written to disk.
        '''
        pass

    def __str__(self):
        return json.dumps(self._d)

if __name__ == '__main__':
    print get_conf()

