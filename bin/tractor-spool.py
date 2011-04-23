#!/usr/bin/env python

"""
Python wrapper around tractor.glue library. Permits the command line launching of
renders onto a tractor render farm.

example usages:

tractor-spool.py nuke -s 1 -e 20 -b 5 -t 8 /path/to/scene/file.nk

tractor-spool.py -i 
Tractor Spool interactive session. Enter the command you wish to execute:
> nuke

Generic Supported Options:

-j --job,		job title	 	default = 'Generic Job'
-r --range		frame range	default '1'
-c --chunk,	chunk size	default = 5
-p --preview, 	preview render frames first 	default = False

Maya Supported Options:

--imagename 	name of the image to render
--project,	path to the maya project
-t --threads, 	threads to use	default = 8
-l --layers,		layers to render	

Nuke Supported Options:

-q --quiet,		quiet mode	default = True
--no-quiet,	don't be quiet	
-t --threads,	threads to use	default = 4
-n --nodes,	nodes to render
-f --fullsize,	force fullsize	default = True

"""

#virtual environment setup -- If you don't use virtualenv then you'll probably want to comment this bit out.
activate_this = '/opt/baseblack/python2.6/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
import os
import getpass
import time
import optparse

from tractor.api import Nuke, Maya, Shake
from tractor.api import Serializer

__version__ = '1.0.0'

def buildArgumentDict( options, filepath ):
	"""Returns two dictionaries, jobargs and command. These are the arguments to the tractor.glue.render derived objects."""
	jobargs = {}
	cmdargs = {}
	
	jobargs['title'] = options.title if options.title else filepath
	if options.imagename:  jobargs['imagename']  = options.imagename	
	if options.chunksize:  jobargs['chunksize']  = options.chunksize	
	
	jobargs['range']  = options.range
	jobargs['preview']  = options.preview
	
	jobargs['user'] = getpass.getuser()
	jobargs['timestamp'] = int( time.time() )

	if options.projectpath: 	jobargs['projectpath']  = options.projectpath
	if options.threads:	 cmdargs['threads']  = options.threads
	if options.layers:	 jobargs['layers']  = options.layers

	cmdargs['quiet'] = options.quiet
	cmdargs['fullsize']  = options.fullsize
	
	if options.threads: 	 cmdargs['threads']  = options.threads
	if options.nodes:	 cmdargs['nodes']  = options.nodes
		
	if options.proxyscale:  cmdargs['proxyscale'] = options.proxyscale
		
	if options.doprogress:
		jobargs['progress'] = 'tkrProgress'
			
	cmdargs['file'] = filepath

	return ( jobargs, cmdargs )
	
# Option fun, or hell it's sometimes a little hard to tell. 
# The options which are supported here are the same as those which are currently exposed through tractor.glue
# As further renderers and options are supported in tractor.glue they should be added to here to give a one stop
# shop for command line rendering.

parser = optparse.OptionParser( version=__version__, usage="%prog [options] [nuke/maya/shake] /path/to/my/scene/file" )
parser.disable_interspersed_args()

parser.add_option("--paused", dest="paused", action="store_true", default=False, help="Send the job to tractor in a paused state. Usefull for queuing jobs." )

parser.add_option("-j","--job", dest="title", type="string", default='', help="Title to name the job by in tractor." )
parser.add_option("-r","--range", dest="range", type="string", default='1', help="Frame range to render. In the form 1-10x2. [Default '1']" )
parser.add_option("-c","--chunk", dest="chunksize", type="int", default=0, help="Size for each chunk for frames. For slow renders reduce this value. [Default maya:5 nuke:10]" )
parser.add_option("-t","--threads", dest="threads", type="int", default=0, help="Number of threads to render with." )
parser.add_option("--preview", action="store_true", dest="preview", default=False, help="perform a preview render of a few frames from the sequence. [Default False]" )
parser.add_option("--progress", action="store_true", dest="doprogress", default=False, help="Name of the progress monitor script to attach to the process. [Default False]" )

mayaOptGroup = optparse.OptionGroup( parser, 'Maya Supported Options' )
mayaOptGroup.add_option("-p","--project", dest="projectpath", type="string", default='', help="Path to the maya project file for this scene." )
mayaOptGroup.add_option("-l","--layers", dest="layers", type="string", default='', help="Names of the layers to render. Written as a comma separated list layer1,layer2,layer3 " )
mayaOptGroup.add_option("--imagename", dest="imagename", type="string", default='default', help="Name to render the image as. [Default 'default']" )

nukeOptGroup = optparse.OptionGroup( parser, 'Nuke Supported Options' )
nukeOptGroup.add_option("-q","--quiet", action="store_true", dest="quiet", default=False, help="Be quiet and do not provide extra output. [Default False]" )
nukeOptGroup.add_option("--no-quiet", action="store_false", dest="quiet", help="Be loud and give lots of message output. [Default True]" )
nukeOptGroup.add_option("-f","--fullsize", action="store_true", dest="fullsize", help="Force the render to be fullsize, ignore proxies. [Default True]" )
nukeOptGroup.add_option("-n","--nodes", dest="nodes", type="string", default='', help="Names of nodes to render." )

shakeOptGroup = optparse.OptionGroup( parser, 'Shake Supported Options' )
parser.add_option("--proxyscale", dest="proxyscale", type="int", default=0, help="Proxy scale to render at. [Default 1]" )

parser.add_option_group( mayaOptGroup )
parser.add_option_group( nukeOptGroup )

options, args = parser.parse_args()

if len(args) < 2:
	print "Incorrect arguments. Please provide the renderer you wish to use and path to the scene file."
	print parser.usage
	sys.exit(1)
	
renderer = args[0]
filepath = args[1]

jobargs, cmdargs = buildArgumentDict( options, filepath )

# I'd really prefer to write this so that an arbitary renderer value can be added without having to update this script. 
# Unfortunatly that may not be easily possible without writing confusing code. 

if renderer == 'maya':
	renderObject = MRfMaya( jobargs, cmdargs )
if renderer == 'nuke':
	renderObject = Nuke( jobargs, cmdargs )
if renderer == 'shake':
	renderObject = Shake( jobargs, cmdargs )
	
renderObject.buildTaskTree()

renderObject.spool( 'tractor', startpaused=options.paused )







