#!/usr/bin/python3
from app import app

# This is the run harness for our main application whose logic
# is in the 'app' directory.
app.run(host='0.0.0.0', debug=True)
