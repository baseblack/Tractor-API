import time		
import subprocess
import getpass
import os, re

from tractor.ordereddict import OrderedDict

__version__ = "3.0.0"

class TaskTree( object ):
	"""Base class for tractor based job scripts. This class should not be called directly."""
	# tasks are stored within a dict within each Task. There is therefore no global 
	# list of all of the nodes in the tree. It would be possible to overload the OrderedDict
	# to create a global name variable to keep track of all insertions from any instance 
	# of the ODict.
	
	def __init__(self):
		pass
	
	def __getattr__( self, attr ):
		try:	
			return self.tasks.__getitem__( attr )
		except KeyError, inst:
			#print "Warning: %s is not a known task id or methodname" % inst
			raise AttributeError
		
	def addTask( self, task ):
		"""A task can be created outside of the job tree and added afterwards or
		it can be created by passing a valid name"""
		
		# Since either a simple string or a Task object may have been provided
		# as an argument the returned task is indexed in the task dictionary by 
		# a key whose setting is dependant on the type of the argument.
				
		if isinstance( task, Task ):
			# Check to see if another task already exists within the job tree
			# with the same name, referenced as task.name. To do this we 
			# match against the list of keys looking for matching names less
			# the "_NodeNNN" that is added. A list of matches is returned 
			# of which we only want the last one. 
			
			# This method is fairly obviously fraught with peril once/if a task 
			# graph becomes too large. If performance becomes too bad then 
			# it may be easier to switch to the simpler, if two nodes are named 
			# the same then they second will be preservered, overwriting the 
			# first.
			
			## Simple Version
			# if isinstance( taskname, Task ):
			#	self.tasks[taskname.name] = taskname
			# 	taskkey = taskname.name
			# else:
			#	self.tasks[taskname] = Task( taskname )
			# 	taskkey = taskname
			#	return self.tasks[taskkey]
								
			regex = re.compile( '(%s_Node\d+$)' % task.name ).search					
			result = [ match.group(1) for l in self.tasks.globalNodeList for match  in [ regex(l) ] if match ]
			
			if result:
				result.sort()
				name, id = result[-1].split('_Node')
				
				task.name = '%s_Node%d' % ( name, int(id)+1 ) 
			else:
				task.name = '%s_Node1' % task.name							# rename the current task's name 
				
			self.tasks[ task.name ] = task
			key = task.name
			
		else:
			# Create a new task with impunity, appending "_Node" to the
			# end of the taskname. In this case 'task' is simply a string stating
			# the name of the task to create.
			
			# The taskname is the unique key for the node in the task tree
			
			regex = re.compile( '(%s_Node\d+$)' % task ).search					# search to see if the task name string provided matches a node
			result = [ m.group(1) for l in self.tasks.keys() for m  in [ regex(l) ] if m]		# it shouldn't be possible to match more that one, but it can happen so a list is built
			
			if result:
				result.sort()						
				name, id = result[-1].split('_Node')		
				
				task= '%s_Node%d' % ( name, int(id)+1 ) 	# if the taskname we've been given exists then we create a new node with an incremented indice.
			else:
				task = '%s_Node1' % task
			
			self.tasks[ task ] = Task( task )
			key = task
			
		self.tasks.globalNodeList.append( key )
		return self.tasks[ key ] 
		
	def printme( self ):
		for task in self.tasks:
			print task, self.tasks[task].commands
			if    self.tasks[task].commands:
				print  "\t", self.tasks[task].commands[0].flags
			self.tasks[task].printme()

	
class Job( TaskTree ):
	"""Simplest way to think of this object is as the start of a job creation script. Global 
	parameters are set here which can effect all the children blah.
	"""
	
	def __init__( self, *args, **kwargs ):		
		self.serialsubtasks = False
		self.tasks = OrderedDict()
		self.title = ""
		self.user = getpass.getuser()  
	
		if 'jobname' in kwargs:
			self.title = jobname
		elif len(args) == 1 :
			self.title = args[0]
			
class Task( TaskTree ):
	# Task names are internally suffixed with "_NodeNNN". As such no
	# task should be named this way intentionally.
	
	def __init__( self, taskname, label="" ):
		self.name = taskname
		self.label = label if label else taskname
		self.service  = None
		self.tasks = OrderedDict()
		self.commands = []
		self.serialsubtasks = False

	def addCmd( self, cmd=None ):
		if cmd:
			self.commands.append( Cmd( executable=cmd ) )
		else:
			self.commands.append( Cmd() )
		return self.commands[-1]

	def addRemoteCmd( self, **kwargs ):
		if 'cmd' in kwargs:
			self.commands.append( RemoteCmd( executable=kwargs['cmd'] ) )
		else:
			self.commands.append( RemoteCmd() )
		return self.commands[-1]
		
	@property
	def lastCmd( self ):
		try:
			return self.commands[-1]
		except:
			return None
		
		
class Cmd( object ):
		
	def __init__( self, *args, **kwargs ):
		"""Simple execution command node. The executable can be passed
		a string containing the name of the program and any flags. Or the
		class can be subclassed for a specific program type."""
	
		self.executable = None
		self.flags = OrderedDict()
		self.remote = False
		self.environ = []
		self.tags = []
		self.shell = None
		
		if 'executable' in kwargs:
			self.executable = kwargs['executable']
	
	def addChaser( self, executable, file ):
		pass
		
	def addPreview( self, executable, file ):
		pass
	
	def addShell( self, shell ):
		self.shell = shell
	
	def addExecutable( self, executable ):
		self.executable = executable
	
	def addOption( self, flag, option='' ):
		if option:
			self.flags[flag] = str(option)
		else:
			self.flags[flag] = ""
			
	def addPipe( self, executable, options='' ):
		if options:
			self.flags['|'] = ''
			self.flags[executable] = options
		else:
			self.flags['|'] = executable
			
class RemoteCmd( Cmd ):
	def __init__( self, *args, **kwargs ):
		Cmd.__init__(self, args, kwargs)
		self.remote = True
		self.service = 'Default'

	
