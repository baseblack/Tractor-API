from tractor.glue.tasktree import  Job, Task
from tractor.glue.render import Render
	
class Shake( Render ):
	"""Simple command line render of a maya scene. Breaks the render up in (n) number of chunks
	based on n = number of frames / chunk size."""
		
	#init needs to set threads and layers
	
	def __init__( self, jobargs, cmdargs ):
		
		super( Shake, self ).__init__( jobargs, cmdargs )
		
		self.job['title']        = 'Shake Job'
		self.command['proxyscale']  = 1
		
		if 'proxyscale' in cmdargs: self.command['proxyscale'] = cmdargs['proxyscale']
		if 'title' in jobargs: self.job['title'] = jobargs['title']
	
	def buildTaskTree( self ):
		
		self.JobObj = Job( self.job['title'] )
		
		maintask = self.mainTask()
		
		self.JobObj.addTask( maintask )
		
	def multiFrameTask( self, f_range ):
		name = 'Main_MultiFr__%s_%s' % ( f_range['first'],f_range['last'] )
		label  = 'Shake : Render : %s-%s :: %s' %(  f_range['first'],f_range['last'], name )

		task = Task( name, label )
		cmd = task.addRemoteCmd()
		
		cmd.addShell( '/bin/bash -c' )
		
		cmd.addExecutable( 'shake' )
		cmd.service = 'ShakeRender'
		cmd.tags = ['shake']
		
		cmd.addOption( '-exec' )	
				
		cmd.addOption( self.command['file'] )
		
		cmd.addOption( '-vv' )	
		
		if self.command['proxyscale']:
			cmd.addOption( '-proxyscale', self.command['proxyscale'] )
		
		if 'step' in f_range:
			cmd.addOption( '-t' , "%s-%sx%s" % ( f_range['first'],f_range['last'],f_range['step'] )  )
		else:
			cmd.addOption( '-t' , "%s-%s" % ( f_range['first'],f_range['last'] )  )
				
		if self.job['progress']:
			cmd.addPipe( self.job['progress'] )
				
		return task
		
	def singleFrameTask( self, frame ):			
		"""
		Single frame render task. Takes a single frame as argument and adds other options from self.cmdargs
		Options are written to the cmdline in the order they are added to the cmd obj.
		"""
		name = 'Main_IndivFr__%s' % frame
		label  = 'Shake : Render : %s :: %s' % ( frame, name )
		task = Task( name, label )
		
		cmd = task.addRemoteCmd()
		
		cmd.addShell( '/bin/bash -c' )
		
		cmd.addExecutable( 'shake' )
		cmd.service = 'ShakeRender'
		cmd.tags = ['shake']
		
		cmd.addOption( '-exec' )	
		
		cmd.addOption( self.command['file'] )
		
		cmd.addOption( '-vv' )	
		
		if self.command['proxyscale']:
			cmd.addOption( '-proxyscale', self.command['proxyscale'] )
		
		cmd.addOption( '-t' , frame )	
		
		if self.job['progress']:
			cmd.addPipe( self.job['progress'] )
		
		return task