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

#Name                              #Version
# tractor-api3.0                    3.0.0-baseblack-r1234
# Nuke6.2-tractor-api3.0      3.0.0-baseblack-r1234
# Maya2011-tractor-api3.0   3.0.0-baseblack-r1234

if [ "$1" == "clean" ]; then
	echo Cleaning...
	rm *.deb
	rm $PWD/dist -r
	exit #quit the script
fi

PLUGIN_NAME=tractor-api
PLUGIN_VERSION=3.0.2
PLUGIN_SHORT_VERSION=3.0
MAYA_VERSION=2011
NUKE_VERSION=6.2
BUILD_NUMBER=2


mkdir -p $PWD/dist/release
mkdir -p $PWD/dist/maya
mkdir -p $PWD/dist/nuke


### MAYA PLUGIN ###
mkdir -p $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/modules
mkdir -p $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/scripts

cp -r src/lib/* $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/scripts/
echo "+ $PLUGIN_NAME $PLUGIN_SHORT_VERSION /opt/baseblack/autodesk/maya/$MAYA_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION" \
	> $PWD/dist/maya/opt/baseblack/autodesk/maya/$MAYA_VERSION/modules/$PLUGIN_NAME-$PLUGIN_SHORT_VERSION.mod

### NUKE PLUGIN ###
mkdir -p $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins
mkdir -p $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/python

cp -r src/lib/* $PWD/dist/nuke/opt/baseblack/foundry/nuke/$NUKE_VERSION/plugins/$PLUGIN_NAME/$PLUGIN_SHORT_VERSION/python

### SHARED LIBRARY ###
mkdir -p $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages
cp -r src/lib/tractor $PWD/dist/release/opt/baseblack/python2.6/lib/python2.6/site-packages/

RELEASE_VERSION="$PLUGIN_VERSION-baseblack-r$BUILD_NUMBER"
REPLACES="${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} (<< ${RELEASE_VERSION})"
DESCRIPTION="Provides access to the tractor-api"


### Construct the debs ###
fpm -n maya${MAYA_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/maya \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"
	
fpm -n nuke${NUKE_VERSION}-${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/nuke \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"
	
fpm -n ${PLUGIN_NAME}${PLUGIN_SHORT_VERSION} \
	-v $RELEASE_VERSION \
	-t deb \
	-s dir \
	-C dist/release \
	--description "$DESCRIPTION" \
	--url "http://tech.baseblack.com/" \
	--replaces "$REPLACES" \
	--maintainer "$DEBEMAIL"