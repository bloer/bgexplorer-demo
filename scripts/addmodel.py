#!/usr/bin/env python
import tarfile
import pymongo
import json
from flask import Config
import sys
from bgexplorer.modeldb import ModelDB
import sys

def addmodel(filename, cfgfile='config.default.py'):
    """Add a model to the database"""
    cfg = Config('')
    cfg.from_pyfile(cfgfile)
    dburi = config.get('MODELDB_URI',None)
    collection = config.get('MODELDB_COLLECTION','bgmodels')
    modeldb = ModelDB(dburi=dburi, collection=collection)
    model = json.load(open(filename))
    modeldb.write_model(model)

if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv)>1 else 'models/hpgedetector.json'
    addmodel(filename)

