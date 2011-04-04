from tractor.glue.tasktree import *


def taskTree():
	
	job = Root('my simple job')

	preflight = job.addTask( 'preflight' )
	preflight.serialsubtasks = True
	preview = preflight.addTask( 'preview' )

	task = preview.addTask( 'frame_1'  )
	task.addCmd( "maya -s 1 -e 1" )

	task = preview.addTask( 'frame_15' )
	task.addCmd( "maya -s 15 -e 15" )

	task = preview.addTask( 'frame_30' )
	task.addCmd( "maya -s 30 -e 30" )

	main = preflight.addTask( 'main' )
	task = main.addTask( 'frame_1-10'  )
	task.addCmd( "maya -s 1 -e 10" )
	task = main.addTask( 'frame_11-20' )
	task.addCmd( "maya -s 11 -e 20" )

	task = main.addTask( 'frame_21_30' )
	task.addCmd()
	cmd  = task.lastCmd
	cmd.addExecutable("maya-render")
	cmd.addOption( "-r", "mr" )
	cmd.addOption( "-rt", 4 )
	cmd.addOption( "-s", 21 )
	cmd.addOption( "-e", 30 )
	cmd.addOption( "-im", job.title )
	cmd.addOption( "/tmp/nuke-1-100-andrew.bunday-1296468388.nk" )

	print "job tasks: ", job.tasks
	print "preflight tasks: ", job.preflight.tasks
	print "preview tasks: ", job.preflight.preview.tasks
	print "preview frame1 tasks: ", job.preflight.preview.frame_1.tasks
	print "preview frame1 cmds: ", job.preflight.preview.frame_1.commands
	print ""
	print "main cmd frame 21-30 :",  job.preflight.main.frame_21_30.lastCmd.executable
	print "main cmd frame 21-30 :",  job.preflight.main.frame_21_30.lastCmd.flags
	


