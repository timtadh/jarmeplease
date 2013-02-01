#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Tim Henderson
#Email: tadh@case.edu
#Copyright (C) 2012 All Rights Reserved
#For licensing see the LICENSE file in the top level directory.

import logging
logging_initialized = False

def initialize_logging():
    global logging_initialized
    if logging_initialized: return
    fmt = '%(levelname)-6s %(name)-17s %(message)s'
    root = logging.root
    root.setLevel(logging.NOTSET)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(fmt))
    root.addHandler(console)
    logging_initialized = True

initialize_logging()

