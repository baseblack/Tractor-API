from tractor.glue.tasktree import *

__version__ = "2.0.0"
	
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
	
class TractorSerializer(  ):

	def __init__(self, obj):
		if isinstance(obj, TaskTree):
			self.tree = obj
			
		self.now =  int( time.time() )  # <-- should alos get this from the tree
		self.spooldir = os.path.join( "/mnt/muxfs/users/spool/tkr", self.tree.user )	
		self.spoolfile = "%s/%s.tkr" % (self.spooldir, self.now)

	def printScript( self ):
		"""A simple dump to stdout debug function"""
		if hasattr( self, 'jobscript'):
			print self.jobscript
			return
		else:
			self.serialize()
			self.printScript()
					
	def serialize( self ):
		if hasattr( self, 'tree' ):
			self.jobscript = self.writeTask( self.tree)
			
	def writeTask( self, task ):
		
		if isinstance( task, Job ):
			output = "\nJob -title { %s } " % task.title
		else:
			#label = task.label if task.label is task.name else "%s : %s" % (task.label, task.name)
			output = "\nTask { %s } -id { %s } " % ( task.label, task.name  )
					
		if task.tasks:
			# iterate through the children
			output += "-subtasks {\n"
			for each in task.tasks:
				output += self.writeTask( task.tasks[each] )
			output += "\n} "
		
		if hasattr(task, 'commands'):
		# finally serialize the current task
		# but only if a command has been set. Tasks can be used to group child tasks.
			if task.commands:
				output += "-cmds { %s \n\t}" % self.writeCmd( task )
											
		return output
				
	def writeCmd( self, task ):
		#hand over the task these commands belong to as it may hold some information needed by each command
		
		output = ""
		for command in task.commands:
			options = "".join([ '%s %s ' % (key, value) for key, value in command.flags.items() ])
			if command.remote:	
				if command.shell:
					output += "\n\t\tRemoteCmd { %s {%s %s} } -service {%s}" % ( command.shell, command.executable, options, command.service)
				else:
					output += "\n\t\tRemoteCmd { %s %s } -service {%s}" % ( command.executable, options, command.service)
			else:
				if command.shell:
					output += "\n\t\tCmd { %s %s %s }" % ( command.shell, command.executable, options)
				else:
					output += "\n\t\tCmd { %s %s }" % ( command.executable, options)
			if command.tags:
				output += " -tags {%s}" % ",".join( command.tags )
		return output

		
	def spool( self, destination, startpaused=False ):
		
		if not hasattr(self, 'jobscript'):
			self.serialize()
		
		if destination is 'stdout':
			print self.jobscript
			
		if destination is 'disk' or destination is 'tractor':
			if not os.path.exists( self.spooldir ):
				os.makedirs( self.spooldir )
				
			p = open( self.spoolfile, "w")
			p.write( self.jobscript )
			p.flush()
			p.close()
			
		if destination is 'tractor':		
			try:
				if startpaused:
					retcode = subprocess.call(["/opt/pixar/tractor-blade/default/tractor-spool.py", "--paused", self.spoolfile])
				else:
					retcode = subprocess.call(["/opt/pixar/tractor-blade/default/tractor-spool.py", self.spoolfile])
			except:
				print "Error Calling tractor-spool.py. Please refer to your Jersey Cow for udder help"
				print retcode