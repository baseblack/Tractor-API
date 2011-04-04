#!/usr/bin/env python
#
# Example script demonstrating building a simple tree of tasks which
# can be executed of iterated over.
#

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

"""
job = { type':'job', 'label':'Simple Job Script', 
		'tasks': { 
					'task1': {
								'type':'task',
								'cmds': [
										'cmd1':{ 
											'type':'RemoteCmd',
											'executable':'echo',
											'options':[
														('hello',),
													  ]	
											}
										'cmd2':{ 
											'type':'RemoteCmd',
											'executable':'echo',
											'options':[
														('hello',),
													  ]	
											}
										]
							},
					'task2': {
								'type':'task',
								'cmds': [
										'cmd1':{ 
											'type':'RemoteCmd',
											'executable':'echo',
											'options':[
														('hello',),
													  ]	
											}
										'cmd2':{ 
											'type':'RemoteCmd',
											'executable':'echo',
											'options':[
														('hello',),
													  ]	
											}
										]
							},
				},
		}

serializer = tractor.glue.serialize.AlfSerializer()
serializer = tractor.glue.serialize.PySerializer()
serializer = tractor.glue.serialize.JSONSerializer()
serializer = tractor.glue.serialize.Pickle()

"""


