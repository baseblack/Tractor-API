from tractor.api.tasktree import Job, Task


def test_taskTree():
	
	job = Job('my simple job')

	preflight = job.addTask( 'preflight' )
	preflight.serialsubtasks = True 
	
	preview = preflight.addTask( 'preview' )

	task = preview.addTask( 'frame_1'  )	# three frames to render from our sequence in the preview
	task.addCmd( "maya -s 1 -e 1" )

	task = preview.addTask( 'frame_15' )
	task.addCmd( "maya -s 15 -e 15" )

	task = preview.addTask( 'frame_30' )
	task.addCmd( "maya -s 30 -e 30" )

	main = preflight.addTask( 'main' )		# and then the main body of the job broken into 3 chunks
	task = main.addTask( 'frame_1-10'  )
	task.addCmd( "maya -s 1 -e 10" )		# this is the simple way to define a command to execute
	task = main.addTask( 'frame_11-20' )
	task.addCmd( "maya -s 11 -e 20" )

	task = main.addTask( 'frame_21_30' )
	task.addCmd()
	cmd  = task.lastCmd
	cmd.addExecutable("maya-render") 	# and this one is a little more convoluted
	cmd.addOption( "-r", "mr" )
	cmd.addOption( "-rt", 4 )
	cmd.addOption( "-s", 21 )
	cmd.addOption( "-e", 30 )
	cmd.addOption( "-im", job.title )
	cmd.addOption( "/tmp/maya-1-100-andrew.bunday-1296468388.ma" )

	print "job tasks: ", job.tasks
	print "preflight tasks: ", job.preflight_Node1.tasks
	print "preview tasks: ", job.preflight_Node1.preview_Node1.tasks
	print "preview frame1 tasks: ", job.preflight_Node1.preview_Node1.frame_1_Node1.tasks
	print "preview frame1 cmds: ", job.preflight_Node1.preview_Node1.frame_1_Node1.commands
	print ""
	print "main cmd frame 21-30 :",  job.preflight_Node1.main_Node1.frame_21_30_Node1.lastCmd.executable
	print "main cmd frame 21-30 :",  job.preflight_Node1.main_Node1.frame_21_30_Node1.lastCmd.flags
	


