This library represents a work in progress wrapper for tractor/alfred job submission scripts. 

The current version works as a command line only callable script, located in /bin or as a python module tractor.api 
which can be imported and used to create a simple submission to tractor.

*Applogies* for the state of the tests and broken UI code. These could be taken out of the repo but since they are not installed with the lib I thought them 
harmless to leave there for reference.

Command Line Use
------------------------------

The library comes with a rather unimaginativly titled script called *tractor-spool.py*. This conflicts badly with the name
which Pixar uses for their submission script, but at the time my mind went blank and now artists are using it at BB and the name
as stuck.

Useage of the cli is fairly easy, although I have to admit that if you decide to run it with all the options you'd like to that it can become a little long winded.
An example for the non-faint of heart::

	tractor-spool.py maya -j '251_gl_060:LS_tran' --imagename='lighting/v005/<RenderLayer>/<RenderPass>/1024x778/251_gl_060_lighting-<RenderLayer>-<RenderPass>-v005' --project=/mnt/muxfs/extratime/251/251_gl_060/maya -r 6-34 -c 1 -t 8 --layers=MasterBeautyLayer,SpecularLayer,BackgroundLayer /mnt/muxfs/extratime/251/251_gl_060/maya/scenes/251_gl_060_lighting/251_gl_060_lighting_v003-06_LS_trans_arms.ma

Virtualenv
~~~~~~~~~~~~

The cli has been written making use of virtualenv to protect it from any changes which can and do often occur. If you don't want to use virtualenv then simply comment out the lines
which activate it and you'll be sorted.<

TaskTree Module
------------------------

This example should demonstrate the general syntax::

	from tractor.glue.tasktree import Job, Task, RemoteCmd
	import tractor.glue.serialize as tractor

	myjob = Job('Simple Job Script')

	task1 = Task( '1', 'Task number 1' )
	cmd1  = task1.addRemoteCmd(service='Default')
	cmd1.addExecutable('echo')
	cmd1.addOption('hello')

	myjob.addTask( task1 )

	task2 = myjob.addTask( '2' )
	cmd2 = RemoteCmd('echo hello')
	task2.addRemoteCmd( cmd2 )

	serializer = tractor.TractorSerializer( myjob )
	serializer.spool( 'stdout' )

TaskTree Node Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Job
   This is the root node for an task tree. It can hold any number of task nodes. 
   
Task
   Individual task nodes. Each task can hold any number of subtasks or commands. 
   
Command/RemoteCommand
   The remote command is a subclass of command, providing additional service information for remote processing.

TractorSerializer 
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than overload the print methods on each of the task tree nodes a serializer instead takes the tasktree when spool'd
iterated over the tree converting the attributes on each of the nodes into a job script. The spool method can either print
out the resulting script to a file on disk, stdout or to disk and then call the pixar tractor-spool.py script to submit the job
to the tractor engine.

The rationale for creating the serializer this way has been to allow room to change the serialization option to JSON or plain 
python pickles easily without the need to make changes to the main task tree code.

Maya/Nuke/Shake Tasktree Convience Classes
--------------------------------------------------------------------

Common task types such as those used to create a Nuke render, or Mental Ray for Maya as encapsulated into helper classes which can imported from tractor.api.
These helpers allow for two dictionaries to be passed as constructor arguments. The first argument contains options for the job as a whole, such as the job name and number of 
frames to render. The command args contains options which are specific to the renderer, such as a string containing a list of node names to render from a nuke script.

Example::

	from tractor.api import Nuke

	jobargs = {'title':'A simple render'} 
	cmdargs = {'file':'/path/to/my/scene/file.nk'}

	renderer = Nuke( jobargs, cmdargs )	
	renderer.buildTaskTree()
	renderer.spool( 'tractor', startpaused=options.paused )
	
GUIs. They don't exist. Yet.
------------------------------------------

On the todo list is the creation of stable ui's for maya/nuke to make submission easier. Presently they are however low on the list since by forcing artists t use the commandline
we've been able to make them think more about what they submit to the farm, rather than throwing dross onto it.