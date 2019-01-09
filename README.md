bgexplorer-demo
===============
This package is a demo showing how to implement and deploy a custom [Background Explorer](https://github.com/bloer/bgexplorer) application instance. It is possible to use this as a starting point for further modification. 

Installation
------------
Installation should be as simple as running
`./scripts/install.sh`
from the project top-level directory.  This will set up a virtual environment 'virtenv' in the current working directory. First 'venv' will be tried, which requires python >=3.4 (I think?), and if that is not found, virtualenv.  If neither of these can be found, installation will abort.  To use a different python than the OS default for installation, one can do
`PYTHON=/path/to/alternate/python ./install.sh`

The application requires access to a mongodb server to store the models and simulation data.  The default configuration file (config.default.py) assumes an unsecured mongodb server running on localhost. This is not recommended for production environments.  To access a secured and/or remote server, change the appropriate URI settings in the config file. 


