from tasktree import Job, Task
from render import Render

class Nuke( Render ):
	"""Simple command line render of a nuke script. Breaks the script up in (n) number of chunks
	based on n = number of frames / chunk size."""
		
	def __init__( self, jobargs, cmdargs ):
		
		super( Nuke, self ).__init__( jobargs, cmdargs )
			
		self.job['title']        = self.command['file']
		self.job['chunksize'] = 10
		self.command['quiet'] = False
		self.command['threads']  = 4
		self.command['nodes']  = ''
		self.command['fullsize']  = True
				
		if 'title' in jobargs: self.job['title'] = jobargs['title']
		if 'chunksize' in jobargs: self.job['chunksize'] = jobargs['chunksize']	
		if 'quiet'       in cmdargs: self.command['quiet'] = cmdargs['quiet']
		if 'threads'   in cmdargs: self.command['threads']  = cmdargs['threads']
		if 'nodes'       in cmdargs: self.command['nodes']  = cmdargs['nodes']
		if 'fullsize' in cmdargs: self.command['fullsize']  = cmdargs['fullsize']
		
	def buildTaskTree( self ):
		
		self.JobObj = Job( self.job['title'] )
		
		qttask = None
		maintask = self.mainTask()
		
		if self.job['quicktime']:
			qttask = quicktimeTask();
			qttask.addTask( maintask )

		else:
			self.JobObj.addTask( maintask )

	
	def multiFrameTask( self, f_range ):
		name = 'Main_MultiFr__%s_%s' % ( f_range['first'],f_range['last'] )
		label  = 'Nuke : Render : %s-%s :: %s' %(  f_range['first'],f_range['last'], name )
		task = Task( name, label )
		
		cmd = task.addRemoteCmd()
		
		cmd.addShell( '/bin/bash -c' )
		
		cmd.addExecutable( 'nuke' )
		cmd.tags = ['nuke']
		cmd.service = 'NukeRender'
				
		if 'quiet' in self.command:
			if self.command['quiet'] == True:
				cmd.addOption( '-q' )
				
		if self.command['fullsize'] == True:
			cmd.addOption( '-f' )
			
		if 'threads' in self.command:
			cmd.addOption( '-m',  self.command['threads'] )
		
		if 'step' in f_range:
			cmd.addOption( '-F' , "%s-%sx%s" % ( f_range['first'],f_range['last'],f_range['step'] )  )
		else:
			cmd.addOption( '-F' , "%s-%s" % ( f_range['first'],f_range['last'] )  )
		
		cmd.addOption( '-x' )

		cmd.addOption( self.command['file'] )
		
		if self.job['progress']:
			cmd.addPipe( self.job['progress'] )
			
		return task
	
				
	def singleFrameTask( self, frame ):			
		"""
		Single frame render task. Takes a single frame as argument and adds other options from self.cmdargs
		Options are written to the cmdline in the order they are added to the cmd obj.
		"""
		name = 'Main_IndivFr__%s' % frame
		label  = 'Nuke : Render : %s :: %s' % ( frame, name )
		task = Task( name, label )
		
		cmd = task.addRemoteCmd()
		cmd.addExecutable( 'nuke' )
		cmd.tags = ['nuke']
		cmd.service = 'NukeRender'
		cmd.addOption( '-x' )
		
		if 'quiet' in self.command:
			if self.command['quiet'] == True:
				cmd.addOption( '-q' )
		
		if self.command['fullsize'] == True:
			cmd.addOption( '-f' )
			
		if 'threads' in self.command:
			cmd.addOption( '-m',  self.command['threads'] )
		
		cmd.addOption( '-F' , frame )
		cmd.addOption( self.command['file'] )
		
		if self.job['progress']:
			cmd.addPipe( self.job['progress'] )
		
		return task