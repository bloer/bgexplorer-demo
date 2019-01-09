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
if ! pip install -r "requirements.txt" ; then
    echo "Error installing dependencies ; exiting" >&2
    exit 2
fi

#exit the virtual environment
deactivate

echo "Setup successful! Use ./scripts/start.sh to start the server"

exit 0


