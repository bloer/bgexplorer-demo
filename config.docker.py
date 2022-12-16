#Docker configuration file for bgexplorer-demo application

## port the application will listen on, read by scripts/start.sh
SERVER_PORT = 5000

## default MongoDB access. Assumes an unsecured mongodb server on localhost
MONGODB_DEFAULT_URI = "mongodb://mongo:27017/bgexplorerdemo"
MONGODB_DEFAULT_DATABASE = "bgexplorerdemo"

## These values are required by the MongoSimsDB
SIMDB_URI = MONGODB_DEFAULT_URI
SIMDB_DATABASE = MONGODB_DEFAULT_DATABASE
SIMDB_COLLECTION = "simulations"

## These values are required by the ModelDB
MODELDB_URI = MONGODB_DEFAULT_URI
MODELDB_COLLECTION = "bgmodels"

## Assay database
ASSAYDB_URI = MONGODB_DEFAULT_URI
ASSAYDB_COLLECTION = "assays"

## Server configuration. See Flask documentation. 
DEBUG = True
TESTING = True
TEMPLATE_AUTO_RELOAD = False
SECRET_KEY = "asdfasl;fkjatjpagm34taspdj"

## Authentication. Set BASIC_AUTH_FORCE=True to require password
BASIC_AUTH_FORCE = False
BASIC_AUTH_REALM = 'BgExplorer Demo'
BASIC_AUTH_USERNAME = 'demo'
BASIC_AUTH_PASSWORD = 'demo'

## Logging
LOGGER_NAME = 'bgexplorerdemo'
LOGFILE = '/var/log/bgexplorerdemo.log'
LOGLEVEL = 10 #DEBUG=10, INFO=20, WARNING=30, ERROR=40
