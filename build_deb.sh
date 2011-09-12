#!/usr/bin/env bash
#
# The tractor-api needs to be available to 3 processes.
#
# 1) Cmdline access via python scripts on in the interactive interpreter
# 2) Within Maya
# 3) Within Nuke
#
# This script creates 3 debs to accomodate these requirements. Packaging the
# api into the appropriate structure for each application.
#
#Name                              #Version
# tractor-api3.0                    3.0.0-baseblack-r1234
# nuke6.2-tractor-api3.0            3.0.0-baseblack-r1234
# maya2011-tractor-api3.0           3.0.0-baseblack-r1234


### CLEAN UP ###
#
#

if [ "$1" == "clean" ]; then
	echo Cleaning...
	rm *.deb
	rm $PWD/dist -r
	exit #quit the script
fi


### BASIC SETUP ###
#
#

if [ ! -n "$PLUGIN_NAME" ];    then   PLUGIN_NAME="tractor-api"; fi
if [ ! -n "$PLUGIN_VERSION" ]; then   PLUGIN_VERSION=4.2.0; fi
if [ ! -n "$PLUGIN_SHORT_VERSION" ]; then   PLUGIN_SHORT_VERSION=`echo $PLUGIN_VERSION | sed 's/\.[0-9]$//'`; fi
if [ ! -n "$BUILD_NUMBER" ];   then   BUILD_NUMBER=1; fi
if [ ! -n "$MAYA_VERSION" ];   then   MAYA_VERSION=2011; fi
if [ ! -n "$NUKE_VERSION" ];   then   NUKE_VERSION=6.3; fi

RELEASE_VERSION="$PLUGIN_VERSION-baseblack-r$BUILD_NUMBER"
DESCRIPTION="Provides access to the tractor-api"

mkdir -p $PWD/dist/release
mkdir -p $PWD/dist/maya
mkdir -p $PWD/dist/nuke


### MAYA PLUGIN ###
# Built for a specific version of maya, a module is created which is loaded using a .mod file
#

mkdir -p $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/modules
mkdir -p $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/scripts
cp -r src/lib/* $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/scripts/

# creates module for maya to load.
echo "+ $PLUGIN_NAME $PLUGIN_SHORT_VERSION /opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION" \
    > $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/modules/$PLUGIN_NAME-$PLUGIN_SHORT_VERSION.mod

REPLACES="maya${MAYA_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} (<< ${RELEASE_VERSION})"

fpm -n maya${MAYA_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/maya \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"


### NUKE PLUGIN ###
#
#

mkdir -p $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins
mkdir -p $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/python

cp -r src/lib/* $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/python

REPLACES="nuke${NUKE_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} (<< ${RELEASE_VERSION})"

fpm -n nuke${NUKE_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/nuke \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"


### SHARED LIBRARY ###
#
#

mkdir -p $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages
cp -r src/lib/tractor $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages/

sed -i "s/VERSION/${PLUGIN_VERSION}/g" $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages/tractor/__init__.py
sed -i "s/muxfs/shows/g" $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages/tractor/__init__.py

REPLACES="${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} (<< ${RELEASE_VERSION})"

fpm -n ${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/release \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"
	
### done ###
