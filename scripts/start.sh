#!/bin/bash

### Start script for bgexplorer-demo

#look for the virtual environment
VIRTENV="virtenv"

if [ ! -d "$VIRTENV" ] ; then
    echo "Error: no virtual environment '$VIRTENV'. Run install.sh first" >&2
    exit 1
fi

GUNICORN=./$VIRTENV/bin/gunicorn
if [ ! -x $GUNICORN ] ; then
    echo "Error: gunicorn is not installed in $VIRTENV" >&2
    exit 2
fi


CFGFILE="$1"
[ -n "$CFGFILE" ] || CFGFILE="config.default.py"
echo "Using config file $CFGFILE"

SERVER_PORT=$(grep "SERVER_PORT" "$CFGFILE" | awk '{print $3}')
[ -n "$SERVER_PORT" ] || SERVER_PORT=5000
echo "Binding to port $SERVER_PORT"

CMD='demo:create_app(cfgfile="'"$CFGFILE"'")'
"$GUNICORN" --reload -b 0.0.0.0:$SERVER_PORT -t 600 -w 4 $CMD





