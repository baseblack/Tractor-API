import time		
import subprocess
import os

from tractor.api.tasktree import TaskTree
from tractor.api.tasktree import Job
from tractor.api.tasktree import Task
from tractor.api.tasktree import RemoteCmd
from tractor.api.tasktree import Cmd

# define for the location of the .tkr spool files. Stored in ../__init__.py
from tractor import SPOOL_DIRECTORY

class SerialError( Exception ):
	pass

class SerializingError( SerialError ):
	"""This exeception is raised when a non tractor oject is passed to
	the dump() method."""
	pass

class UnserializingError( SerialError ):
	"""There was an error in unserializing a tractor script into a tractor
	object. Could be a bunch of reasons really."""
	pass
	
class SerializerBase( object ):
	"""The base class for the serializer handles the iteration of the job tree and writing of the serialized
	tree to disk. It handles calling the submission script provided by the render manager"""
	
	def __init__(self, obj):
		if isinstance(obj, TaskTree):
			self.tree = obj
						
		self.now =  int( time.time() )  # <-- should alos get this from the tree
		self.spooldir = os.path.join( SPOOL_DIRECTORY, self.tree.user )	
		self.spoolfile = "%s/%s.tkr" % (self.spooldir, self.now)
		
		super( SerializerBase, self).__init__()
				
	def serialize( self ):
		if hasattr( self, 'tree' ):
			self.jobscript = self.writeNode( self.tree)
				
	def writeNode( self, node ):
			
		if isinstance( node, Job ):
			output = self.writeJob( node )
		elif isinstance( node, Task ):
			output = self.writeTask( node )

		return output
	
	def writeJob( self, job ):		
		
		output = self.jobtitle( job ) 

		if job.after		: output += self.subtasks( job )
		if job.globalvars	: output += self.init( job ) 	
		if job.tasks 		: output += self.subtasks( job )	
		if job.atleast > 0	: output += self.subtasks( job )
		if job.atmost > 0 	: output += self.subtasks( job )
		if job.tags 		: output += self.tags( job )
		if job.service 		: output += self.service( job )
				
		return output
			
	def writeTask( self, task ):
		
		output = self.tasktitle( task )
			
		if task.serialsubtasks : output += self.serialsubtasks( task )
		if task.tasks : output += self.subtasks( task )
		if task.commands : output += self.commands( task )
											
		return output
		
	def writeCmds( self, task ):
		#hand over the task these commands belong to as it may hold some information needed by each command
		
		for command in task.commands:
			options = "".join([ '%s %s ' % (key, value) for key, value in command.flags.items() ])
			
			if command.remote:	
				output = self.writeRemoteCmd( command, options )
			else:
				output = self.writeLocalCmd( command, options )
				
			if command.tags:
				self.tags( command )
				
		return output
		
	def spool( self, destination=None, startpaused=True, user=None ):
		"""The destination can be any one of 'stdout'/'tractor'/'disk'. To launch the render but not have it
		start immediately set startpaused to True. To launch the job to run as another user set user to the 
		username of the person to run as.
		"""
		
		if not hasattr(self, 'jobscript'):
			self.serialize()
		
		if destination is 'disk' or destination is 'tractor':
			if not os.path.exists( self.spooldir ):
				os.makedirs( self.spooldir )
				
			p = open( self.spoolfile, "w")
			p.write( self.jobscript )
			p.flush()
			p.close()
			
		if destination is 'tractor':	
			argumentlist = ["/opt/pixar/tractor-blade/default/tractor-spool.py"]
			if startpaused:
				argumentlist.append( "--paused" )
			if user:
				argumentlist.append( "--user=%s" % user )

			argumentlist.append( self.spoolfile )
			try:
				retcode = subprocess.call( argumentlist )
			except:
				print "Error Calling tractor-spool.py. Please refer to your Jersey Cow for udder help"
				
		if destination is 'stdout' or not destination :
			print self.jobscript
	
class Serializer( SerializerBase ):
	"""Tractor based serialization class. When spool() is called on a job object the 
	tree of tasks is walked down, serializing all nodes in the tree into their alf script
	equivalents.
	"""

	def __init__( self, obj ):
		self.jobSerializableAttrs  = [ 'globalvars', 'tags', 'tasks' ]
		self.taskSerializableAttrs = {}
		self.cmdSerializableAttrs = {}

		super(Serializer, self).__init__( obj )


	######################################
	#
	# Serialization methods. 
	#
	######################################
	
	def atleast( self, node ):
		"""returns the minimum number of procs for the node:\n\n\t "-atleast %%d" """
		return " -atleast %d" % node.atleast
	
	def atmost( self, node ):
		"""eturns the maximum number of procs for the node:\n\n\t  "-atmost %%d" """
		return " -atmost %d" % node.atmost
	
	def chaser( self, node ):
		"""returns the command to display ouput once a task has completed:\n\n\t "-chaser {%%s} """
		return " -chaser {%s}" % node.chaser	
	
	def commands( self, node ):
		"""returns a string containing commands for  a task:\n\n\t "-cmds { command/s }" """
		return " -cmds { %s \n\t}" % self.writeCmds( node )
	
	def init( self, node ):
		"""Sets global job variables using the Assign keyworkd:\n\n\t "-init{ Assign A {B} }" """
		output + " -init { "
		for var in node.globalvars:
			output += "\nAssign %s {%s}" % ( var, node.globalvars[var] )
		output += "\n}"
	
	def jobtitle( self, node ):
		"""returns a string containing the  start of an alf script:\n\n\t "Job -title {example job}" """
		return "\nJob -title { %s } " % node.title
	
	def preview( self, node ):
		"""returns the command to display output during processing:\n\n\t "-preview {%%s} """
		return " -preview {%s}" % node.preview
	
	def serialsubtasks( self, node ):
		"""returns a flag for if the children of this node should be executed in serial:\n\n\t "-serialsubtasks 1" """
		return " -serialsubtasks 1"
		
	def service( self, node ):
		"""returns the list of services required for the task/job:\n\n\t "-service { servicename,servicename }" """
		return " -service {%s}" % node.service	
	
	def subtasks( self, node ):
		"""returns a string containing all of the subtasks for the current node:\n\n\t "-subtasks{ (N) }" """
		output = " -subtasks {\n"
		
		for each in node.tasks:
			output += self.writeNode( node.tasks[each] )
		output += "\n}"
	
		return output
	
	def tags( self, node ):
		"""returns tags for a task or job node:\n\n\t "-tags { tag/s }" """
		return " -tags {%s}" % ",".join( node.tags )

	def tasktitle( self, node ):
		"""returns a string containing the  definition of a task:\n\n\t "Task {name } -id {1234}" """
		return "\nTask { %s } -id { %s } " % ( node.label, node.name  )
	
	def writeLocalCmd( self, command, options ):
		"""writes out a local command:\n\n\t "Cmd { executable options[] }" """
		
		if command.shell:
			return "\n\t\tCmd { %s %s %s }" % ( command.shell, command.executable, options)
		else:
			return "\n\t\tCmd { %s %s }" % ( command.executable, options)		
		
	def writeRemoteCmd( self, command, options ):
		"""writes out a remote command:\n\n\t "RemoteCmd { executable options[] }" """		
		
		if command.shell:
			return "\n\t\tRemoteCmd { %s {%s %s} } -service {%s}" % ( command.shell, command.executable, options, command.service)
		else:
			return "\n\t\tRemoteCmd { %s %s } -service {%s}" % ( command.executable, options, command.service)

	
	