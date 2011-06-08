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
	
class Serializer(  ):
	"""Tractor based serialization class. When spool() is called on a job object the 
	tree of tasks is walked down, serializing all nodes in the tree into their alf script
	equivalents.
	"""

	jobSerializableAttrs  = [ 'globalvars', 'tags', 'tasks' ]
	taskSerializableAttrs = {}
	cmdSerializableAttrs = {}

	def __init__(self, obj):
		if isinstance(obj, TaskTree):
			self.tree = obj
						
		self.now =  int( time.time() )  # <-- should alos get this from the tree
		self.spooldir = os.path.join( SPOOL_DIRECTORY, self.tree.user )	
		self.spoolfile = "%s/%s.tkr" % (self.spooldir, self.now)
				
	def serialize( self ):
		if hasattr( self, 'tree' ):
			self.jobscript = self.writeTask( self.tree)
	
	
	def writeNode( self, node ):
			
		if isinstance( task, Job ):
			output = self.writeJob( task )
		elif isinstance( task, Task ):
			output = self.writeTask( task )
	
	##### serialization #####
	
	def subtasks( self, node ):
		output = "-subtasks {\n"
		
		for each in node.tasks:
			output += self.writeNode( node.tasks[each] )
		output += "\n}"
	
		return output
	
	def commands( self, node ):
		return "-cmds { %s \n\t}" % self.writeCmds( task )
		
	def init( self, node ):
		output + "-init { "
		for var in node.globalvars:
			output += "\nAssign %s {%s}" % ( var, node.globalvars[var] )
		output += "\n}"
			
	def tags( self, node ):
		return " -tags {%s}" % ",".join( node.tags )
			
	##### node iteration #####		
			
	def writeJob( self, job ):		
		
		output = "\nJob -title { %s } " % job.title

		if job.globalvars : 
			output += self.init( job ) 	
			
		if job.tags:
			output += self.tags( job )
		
		if job.tasks:
			output += self.subtasks( job )
		
		return output
			
	def writeTask( self, task ):
		
		output = "\nTask { %s } -id { %s } " % ( task.label, task.name  )
			
		if task.serialsubtasks :
			output += "-serialsubtasks 1 "
					
		if task.tasks:
			output += self.subtasks( task )
		
		if task.commands:
			output += self.commands( task )
											
		return output

	def writeRemoteCmd( self, command, options ):
		
		if command.shell:
			return "\n\t\tRemoteCmd { %s {%s %s} } -service {%s}" % ( command.shell, command.executable, options, command.service)
		else:
			return "\n\t\tRemoteCmd { %s %s } -service {%s}" % ( command.executable, options, command.service)

	def writeLocalCmd( self, command, options ):
		
		if command.shell:
			return "\n\t\tCmd { %s %s %s }" % ( command.shell, command.executable, options)
		else:
			return "\n\t\tCmd { %s %s }" % ( command.executable, options)		
	
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