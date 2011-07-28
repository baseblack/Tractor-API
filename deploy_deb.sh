#!/usr/bin/env bash
#
# Pushes a debian package into the apt repostory
#

if [ $# -ne "2" ]; then
    if [ "$COMPONENT" == "" ]; then
        echo "COMPONENT:"
        read COMPONENT
    else
        echo "component -> $COMPONENT"
    fi
    
    if [ "$DEB_FILE" == "" ]; then
        echo "DEB_FILE:"
        read DEB_FILE
    else
        echo "package file -> $DEB_FILE"
    fi
else
    COMPONENT=$1
    DEB_FILE=$2
fi

reprepro -V --basedir /home/tech/repositories/apt/baseblack --component $COMPONENT includedeb ubuntu-lucid $DEB_FILE