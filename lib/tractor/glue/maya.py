from tractor.glue.tasktree import  Job, Task
from tractor.glue.render import Render

class MRfMaya( Render ):
	"""Simple command line render of a maya scene. Breaks the render up in (n) number of chunks
	based on n = number of frames / chunk size."""
		
	#init needs to set threads and layers
	
	def __init__( self, jobargs, cmdargs ):
		
		super( MRfMaya, self ).__init__( jobargs, cmdargs )

		self.job['title']        = 'MRfMaya Job'
		self.job['projectpath'] = None
		self.job['layers'] = None
		self.command['threads'] = 8
				
		if 'title' in jobargs: self.job['title'] = jobargs['title']
		if 'projectpath'  in jobargs: self.job['projectpath'] = jobargs['projectpath']
		if 'threads'         in cmdargs: self.command['threads'] = cmdargs['threads']
		if 'layers'           in jobargs: self.job['layers'] = jobargs['layers']

	def buildTaskTree( self ):
		
		self.JobObj = Job( self.job['title'] )
		
		maintask = self.mainTask()
		
		self.JobObj.addTask( maintask )
		
	def multiFrameTask( self, f_range ):
		name = 'Main_MultiFr__%s_%s' % ( f_range['first'],f_range['last'] )  #Main will be replaced with LAYERNAME in layer based renders
		label  = 'Maya : Render : %s-%s' %(  f_range['first'],f_range['last'] )

		task = Task( name, label )
		cmd = task.addRemoteCmd()
		
		#cmd.addShell( '/bin/bash -c' )
		
		cmd.addExecutable( 'maya-render' )
		cmd.service = 'MRfMRender'
		cmd.tags = ['maya']
				
		cmd.addOption( '-r', "mr" )
		cmd.addOption( '-v', 5 )
		cmd.addOption( '-im',  self.job['imagename'] )
		
		if self.job['projectpath']:
			cmd.addOption( '-rd',  ('%s/images') % self.job['projectpath']  )
		
		if 'threads' in self.command:
			cmd.addOption( '-rt',  self.command['threads'] )
		
		cmd.addOption( '-s' , "%s" % f_range['first']  )
		cmd.addOption( '-e' , "%s" % f_range['last']  )
		
		if 'step' in f_range:
			cmd.addOption( '-b' , "%s" % f_range['step']   )
			
		if self.job['layers']:
			cmd.addOption( '-rl', self.job['layers'] )
			
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
		label  = 'Maya : Render : %s :: %s' % ( frame, name )
		task = Task( name, label )
		
		cmd = task.addRemoteCmd()
		
		#cmd.addShell( '/bin/bash -c' )
		
		cmd.addExecutable( 'maya-render' )
		cmd.service = 'MRfMRender'
		cmd.tags = ['maya']
	
		cmd.addOption( '-r', "mr" )
		cmd.addOption( '-v', 5 )
		cmd.addOption( '-im',  self.job['imagename'] )
		
		if self.job['projectpath']:
			cmd.addOption( '-rd',  ('%s/images') % self.job['projectpath']  )
	
		if 'threads' in self.command:
			cmd.addOption( '-rt',  self.command['threads'] )
			
		cmd.addOption( '-s' , frame )
		cmd.addOption( '-e' , frame )
		
		if self.job['layers']:
			cmd.addOption( '-rl', self.job['layers'] )
		
		cmd.addOption( self.command['file'] )
		
		if self.job['progress']:
			cmd.addPipe( self.job['progress'] )
		
		return task