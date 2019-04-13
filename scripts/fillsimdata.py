#!/usr/bin/env python
import tarfile
import pymongo
import json
from flask import Config
import sys

def insertall(filename, dbcollection):
    ninsert = 0
    with tarfile.open(filename) as tf:
        for member in tf:
            if member.isfile():
                print("extracting", member.name)
                with tf.extractfile(member.name) as mf:
                    obj = json.load(mf)
                    try:
                        dbcollection.insert(obj)
                    except pymongo.errors.DuplicateKeyError:
                        print("Entry",obj.get('_id'),"already in db")
                    else:
                        ninsert += 1
    print("Inserted",ninsert,"entries")
    return ninsert

def getcollection(cfgfile='config.default.py'):
    cfg = Config('')
    cfg.from_pyfile(cfgfile)
    client = pymongo.MongoClient(cfg['SIMDB_URI'])
    db = client[cfg['SIMDB_DATABASE']]
    collection = db[cfg['SIMDB_COLLECTION']]
    return collection

if __name__ == '__main__':
    if(len(sys.argv) <2):
        print("Usage:",sys.argv[0],"<tarfile> [<configfile>]")
        sys.exit(1)

    dbcoll = getcollection() if len(sys.argv)<3 else getcollection(sys.argv[2])
    insertall(sys.argv[1], dbcoll)
    sys.exit(0)

