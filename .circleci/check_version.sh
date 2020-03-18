#!/bin/bash

# Collect the name and version from `pyproject.toml`
NAME=$(cat pyproject.toml | grep name | sed 's/"//g' | awk '{print $3}')
VERSION=$(cat pyproject.toml | grep version | sed 's/"//g' | awk '{print $3}')

# Running `pip install packaganame==` returns this in STDERR
#   ERROR: Could not find a version that satisfies the requirement packagename== (from versions: 0.1.0, 0.1.1, 0.1.2)

# |& pipes into STDOUT both STDOUT and STDERR
pip install "$NAME==" |& grep $VERSION

# The return of the command above will naturally be 0 if there is a line and 1 if there isn't
# $? is the status code of the previous command
if [ $? = 1 ]
then
    echo "Version is new"
    exit 0 # This is good, we need this because otherwise, the script would end with 1
else
    echo "Error, this version has been pushed already ($VERSION)"
    exit 1 # Anything above 0 would cause this to break
fi

