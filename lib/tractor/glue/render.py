import re
import sys
from tractor.ordereddict import OrderedDict
from tractor.glue.tasktree import Task
import  tractor.glue.serialize as serialize

__version__ = "2.0.0"		
			
class Job( object ):
	"""Sets up the expected minimum dictionary of arguments expected for an empty job. """
	
	def __init__( self, jobargs ):
				
		self.job = dict()
				
		# default values @optionally have these read from a config....
		self.job['title']        = 'Generic Job'
		self.job['imagename'] = 'default'
		self.job['user']          = 'unknown.soldier'
		self.job['range']        = '1'
		self.job['chunksize'] = 5
		self.job['timestamp']  = ''
		self.job['weight']        = '2'
		self.job['check']          = False
		self.job['quicktime']  = False
		self.job['preview']      = False
		self.job['progress']    = ''
				
		if 'title'         in jobargs: self.job['title']  = jobargs[ 'title' ]
		if 'imagename' in jobargs: self.job['imagename']  = jobargs[ 'imagename' ]
		if 'user'           in jobargs: self.job['user']  = jobargs[ 'user' ]
		if 'range'         in jobargs: self.job['range']  = jobargs[ 'range' ]
		if 'chunksize' in jobargs: self.job['chunksize']  = jobargs[ 'chunksize' ]
		if 'timestamp' in jobargs: self.job['timestamp']  = jobargs[ 'timestamp' ]
		if 'weight'       in jobargs: self.job['weight']  = jobargs[ 'weight' ]
		if 'check'         in jobargs: self.job['check']  = jobargs[ 'check' ]
		if 'quicktime' in jobargs: self.job['quicktime']  = jobargs[ 'quicktime' ]
		if 'preview'     in jobargs: self.job['preview']  = jobargs[ 'preview' ]	
		if 'progress'     in jobargs: self.job['progress']  = jobargs[ 'progress' ]		
			
class Command( object ):
	"""Sets up the expected minimum dictionary of arguments expected for an empty command. """
	
	def __init__( self, cmdargs ):
				  
		self.command = dict()
		self.command['file'] = cmdargs[ 'file' ] if 'file' in cmdargs else None

class Render( Job, Command ):
	
	def __init__( self, jobargs, cmdargs ):
		
		Job.__init__( self, jobargs )
		Command.__init__( self, cmdargs )
			
		self.splitFrameRange()
			
	def splitFrameRange( self ):

		self.job['framerange'] = []
		
		for each_range in self.job['range'].split(',') :
		
			this = OrderedDict()
			
			args = re.findall(  "([0-9]+)(-)?([0-9]+)?(x)?([0-9]+)?"  , each_range )[0]
						
			if len( args[0] ):  this['first'] = int( args[0] );
			if len( args[1] ) and len( args[2] ):   this['last'] = int( args[2] );
			if len( args[3] ) and len( args[4] ):   this['step'] = int( args[4] );
						
			self.job['framerange'].append( this )
			
	def previewTask( self ):
		
		previewtask = Task('Preview__')
		return previewtask	
	
	def mainTask( self ):
	
		maintask = Task('Main__')
		
		for thisrange in self.job['framerange']:   # ['1-10x2','11-20',25]
			if 'last' in thisrange:
				rangelength = thisrange['last'] - thisrange['first']  + 1  #+1 for inclusive range
				
				if rangelength > self.job['chunksize'] and self.job['chunksize'] != 0:
					
					#number of frames is greater than a single chunk. need to split
					chunkCount        = int( rangelength / self.job['chunksize'] )
					chunkRemainder = rangelength % self.job['chunksize']
										
					for chunk in range( chunkCount ):                                 #frame range for the chunk (firstframe, lastframe, step)
						chunkrange = dict()
						chunkrange['first'] = thisrange['first'] + ( chunk * self.job['chunksize'] )
						chunkrange['last']   = chunkrange['first']  + ( self.job['chunksize'] - 1 ) # inclusive of the first frame
						
						if 'step' in thisrange:
							chunkrange['step'] = thisrange['step']
						maintask.addTask( self.multiFrameTask( chunkrange ) )	# this is not strictly correct. If  len(chunkrange)==1 then a single frame should be used.				
						
					if chunkRemainder :
						if chunkRemainder > 1:
							remainder_range = {}
							remainder_range['first'] = thisrange['first'] + ( self.job['chunksize'] * chunkCount )
							remainder_range['last']   = thisrange['last']
							if 'step' in thisrange:
								remainder_range['step'] = thisrange['step']
							maintask.addTask( self.multiFrameTask( remainder_range ) )
							
						else:
							maintask.addTask( self.singleFrameTask( thisrange['last'] ) )
						
				else:
					maintask.addTask( self.multiFrameTask( thisrange ) )         #no chunking is required for the range
				
			else:
				maintask.addTask( self.singleFrameTask( thisrange['first'] ) )  #single frame task
		
		return maintask

	def spool( self, destination, startpaused=False ):
		
		#try:
		tractor = serialize.TractorSerializer( self.JobObj )	
		tractor.serialize()
		tractor.spool( destination, startpaused )    #where destination is either 'stdout', 'disk', or 'tractor'
		#except:
		#	print "Error during spooling. Phew, could have segfaulted there."
	
	
def quicktimeTask( self ):
	"""To generate a quicktime of the completed frames at the end of the render process"""
	
	task = Task('Quicktime__')
	task.service = 'QTProRes422'
	self.serialsubtask = True
	task.addCmd( 'echo "making a quicktime..."')
	
	return task		


