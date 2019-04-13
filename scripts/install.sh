#!/bin/bash
### Installation script for bgexplorer-demp package. 
### See README.md for instructions

[ -n "$PYTHON" ] || PYTHON=$(which python)

echo "Using PYTHON=$PYTHON"

VIRTENV="virtenv"
if [ ! -d "$VIRTENV" ] ; then
    echo "Creating virtual environment $VIRTVENV"
    #first try venv
    if ! $PYTHON -m venv $VIRTENV ; then
	if ! virtualenv $VIRTENV ; then
	    echo "Unable to setup virtual environment; exiting" >&2
	    exit 1
	fi
    fi
fi

source $VIRTENV/bin/activate

echo "Installing required dependencies"
if ! pip install --process-dependency-links -r "requirements.txt" ; then
    echo "Error installing dependencies ; exiting" >&2
    exit 2
fi

echo "Populating simulation database"
if ! $(dirname $0)/fillsimdata.py simdata.tar.gz ; then
    echo "Error populating simulation data" >&2
    exit 3
fi

echo "Adding demo model"
if ! $(dirname $0)/addmodel.py models/hpgedetector.json ; then
    echo "Error adding model" >&2
    exit 4
fi

#exit the virtual environment
deactivate

echo "Setup successful! Use ./scripts/start.sh to start the server"

exit 0


