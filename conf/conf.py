#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import sys, os, json, logging
import cStringIO as sio

import log_conf
log = logging.getLogger('conf')

def encode(d):
    new = dict()
    for k,v in d.iteritems():
        if isinstance(v, list):
            l = list()
            for i in v:
                if isinstance(i, unicode):
                    l.append(i.encode('utf-8'))
                else:
                    l.append(i)
            v = l
        if isinstance(k, unicode): k = k.encode('utf-8')
        if isinstance(v, unicode): v = v.encode('utf-8')
        new[k] = v
    return new

def make_list_get(d, key):
    def get(self):
        return [
            Section(i) for i in d[key] if isinstance(i, dict)
        ] + [
            i for i in d[key] if not isinstance(i, dict)
        ]
    return get
def make_sec_get(d, key):
    def get(self):
        return Section(d[key])
    return get
def make_val_get(d, key):
    def get(self):
        return d[key]
    return get
def _set(self,k,v): raise RuntimeError, 'Operation Not Supported'
def _del(self): raise RuntimeError, 'Operation Not Supported'

class Section(object):

    def __init__(self, d):

        self.__keys = list()
        for k,v in d.iteritems():
            if not (isinstance(v, dict) or isinstance(v, list)):
                p = property(make_val_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, dict):
                p = property(make_sec_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            elif isinstance(v, list):
                p = property(make_list_get(d, k),_set,_del,
                    'Property for interacting with "%s"' % k)
            object.__setattr__(self, k, p)
            self.__keys.append(k)

    def __iter__(self):
        for k in self.__keys:
            yield k

    def iteritems(self):
        for k in self.__keys:
            yield k, getattr(self, k)

    def __repr__(self):
        l = list()
        for name in dir(self):
            a = object.__getattribute__(self, name)
            if type(a) == property: l.append((name, str(a.fget(self))))

        return str(dict(l))

    def __getattribute__(self, name):
        if type(object.__getattribute__(self, name)) == property:
            return object.__getattribute__(self, name).fget(self)
        return object.__getattribute__(self, name)

    def __getitem__(self, name):
        return self.__getattribute__(name)


class BaseConfig(object):

    def __new__(cls, schema, path, **kwargs):
        self = super(BaseConfig, cls).__new__(cls)
        self.schema = schema
        self._d = self.__process_path(path)
        return self

    def __init__(self, schema, *paths, **kwargs):
        self._expose_dict()

    def __process_path(self, path):
        log.debug('loading config file at: %s' % path)
        conf = dict()
        if os.path.exists(path):
            with open(path, 'rb') as f:
                try:
                    conf = json.load(f, object_hook=encode)
                except ValueError, e:
                    log.exception(
                        "The config file at '%s' appears to be corrupted."%
                        path
                    )
                    sys.exit(1)
                try:
                    conf = self.verify(conf)
                except Exception, e:
                    log.exception(e)
                    sys.exit(2)
        log.debug(' '*4 + str(conf))
        return conf

    def __iter__(self):
        for k in self._exposed:
            yield k

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return self._exposed.__getattribute__(name)

    def __getitem__(self, name):
        return self.__getattribute__(name)

    ## ## private methods ## ##
    def _expose_dict(self):
        self._exposed = Section(self._d)

    def verify(self, d):
        '''
        Assert that d matches the schema
        @param d = the dictionary
        @param allow_none = allow Nones in d
        @returns the processed object
        '''
        def proc(Type, v2):
            '''process 2 values assert they are of the same type'''
            #print 'proc>', v1, v2
            if isinstance(Type, dict):
                return dict(procdict(Type, v2))
            elif isinstance(Type, list):
                return list(proclist(Type, v2))
            else:
                if v2 is None:
                    return Type()
                return Type(v2)
        def proclist(t, d):
            '''process a list type'''
            assert len(t) == 1
            if not isinstance(d, list):
                msg = ("Expected a <type 'list'> got %s" % type(d))
                raise AssertionError, msg
            v1 = t[0]
            for v2 in d:
                #print v1, v2
                yield proc(v1, v2)
        def procdict(t, d):
            '''process a dictionary type'''
            if not isinstance(d, dict):
                raise AssertionError, "Expected a <type 'dict'> got %s, '%s'"\
                                      % (type(d), str(d))
            tkeys = set(t.keys());
            dkeys = set(d.keys());
            if '__undefinedkeys__' in tkeys:
                v1 = t['__undefinedkeys__']
                for k, v2 in d.iteritems():
                    yield (k, proc(v1, v2))
            else:
                for k in dkeys:
                    try:
                        assert k in tkeys
                    except:
                        msg = (
                          'Unexpected name, "%s". The name must be in %s'
                        ) % (k, str(tkeys))
                        raise AssertionError, msg
                for k in dkeys:
                    #print '> ', k
                    v1 = t[k]
                    v2 = d[k]
                    try:
                        yield (k, proc(v1, v2))
                    except Exception, e:
                        raise e.__class__, "error with %s -> %s" % (k, ', '.join(e.args))
                for k in (tkeys - dkeys):
                    v1 = t[k]
                    try:
                        yield (k, proc(v1, None))
                    except Exception, e:
                        raise e.__class__, "error with %s -> %s" % (k, ', '.join(e.args))
        return proc(self.schema, d)

