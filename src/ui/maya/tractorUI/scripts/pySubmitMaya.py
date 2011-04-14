import maya.cmds as cmds
import maya.mel as mel

import os
import getpass
import time

import tractor.glue.render as tractor
	
class pyRenderDialog():
	def __init__( self ):
		
		class ui():
			def __init__(self):
				pass
		
		self.ui = ui()
		self.buildWindow()
		self.setupControls()
		self.sceneInfo = getSceneInfo()
		
				
	def buildWindow( self ):
		self.window = cmds.window( title="Submit to Farm", iconName='Render', widthHeight=(387, 450) )
		
		cmds.columnLayout(rowSpacing=20, columnOffset=['both',20] )
		
		cmds.setParent("..")
		
		cmds.rowColumnLayout( numberOfColumns=2, columnAttach=(1, 'right', 0), columnWidth=[(1, 100), (2, 250)] )
		
		
		# render globals
		cmds.text( label = 'Job Name' )
		self.ui.jobname = cmds.textField()
		
		cmds.text( label = 'Render Name' )
		self.ui.rendername = cmds.textField()
		
		cmds.text( label = 'Frame Range' )
		self.ui.framerange = cmds.textField()
		
		cmds.text( label = 'Chunk Size' )
		self.ui.chunksize = cmds.intSliderGrp( field=True, maxValue=100, step=15,fieldStep=15,sliderStep=15 )
		
		cmds.text( label = 'Threads' )
		self.ui.threads = cmds.intSliderGrp( field=True, minValue=1, maxValue=16, fieldStep=2, value=8 )
		
		cmds.text( label = '' )
		self.ui.globals = cmds.button( label='Open Render Settings')
		
		# select the layers to render
		cmds.text( label = 'Render Layers' )
		self.ui.renderlayers = cmds.textScrollList( numberOfRows=8, allowMultiSelection=True,  append=['default'], selectItem='default', showIndexedItem=1 )
				
		cmds.text( label = '' )
		self.ui.refresh = cmds.button( label='refresh' )
		
		
		# general options for the render manager
		cmds.text( label = 'Options' )
		self.ui.options = cmds.checkBoxGrp( numberOfCheckBoxes=2, labelArray2=['Check Outputs', 'Generate Quicktime'] )
		cmds.text( label = 'Process' )
		self.ui.process = cmds.radioButtonGrp( labelArray4=['Light', 'Medium', 'Heavy', 'Sumo'], select=2, numberOfRadioButtons=4, columnWidth4=[60,60,60,60] )
		
		cmds.setParent("..")
		
		
		# render button
		cmds.columnLayout( columnOffset=['both',20] )
		self.ui.render = cmds.button( label='Render', width=330, height=50 )
	
	
	def setupControls( self ):
		
		cmds.textField( self.ui.rendername, edit=True, enterCommand=('cmds.setFocus(\"' + self.ui.framerange + '\")') )
		cmds.textField( self.ui.framerange, edit=True, enterCommand=('cmds.setFocus(\"' + self.ui.chunksize + '\")') )
		
		cmds.button( self.ui.refresh, edit=True, command=self.refreshLayers )
		cmds.button( self.ui.globals, edit=True, command=self.launchGlobalsWindow )
		cmds.button( self.ui.render, edit=True, command=self.render )
		
		if cmds.getAttr('defaultRenderGlobals.imageFilePrefix'):
			self.rendername =  cmds.getAttr('defaultRenderGlobals.imageFilePrefix')
					
		if cmds.getAttr('defaultRenderGlobals.animation'):
			first  = cmds.getAttr('defaultRenderGlobals.startFrame')
			last  = cmds.getAttr('defaultRenderGlobals.endFrame')
			step = cmds.getAttr('defaultRenderGlobals.byFrameStep')
			self.framerange = "%d-%dx%d" % ( first, last, step)
		else:
			first  = cmds.getAttr('defaultRenderGlobals.startFrame')
			self.framerange = "%d" % first
			
		if hasattr(self,'rendername'):
			cmds.textField( self.ui.rendername, edit=True, text=self.rendername )
		else:
			cmds.textField( self.ui.rendername, edit=True, text="[not set; using scene name]" )
		if hasattr(self,'framerange'):
			cmds.textField( self.ui.framerange, edit=True, text=self.framerange )
	
	def launchGlobalsWindow( self, clicked ):
		mel.eval('unifiedRenderGlobalsWindow;')
		
	def refreshLayers( self, clicked ):
		
		print "refreshing..."
		
		cmds.textScrollList( self.ui.renderlayers, edit=True, removeAll=True )
		renderableLayers = getRenderableLayers(self.sceneInfo)
		
		print renderableLayers
		if renderableLayers:
			for layer in renderableLayers:
				cmds.textScrollList( self.ui.renderlayers, edit=True, append=layer )

	def show( self ):
		cmds.showWindow( self.window )
		self.refreshLayers(True)
		
	def render( self, clicked ):
		self.jobname = cmds.textField( self.ui.jobname, query=True, text=True )
		self.rendername = cmds.textField( self.ui.rendername, query=True, text=True )
		self.framerange = cmds.textField( self.ui.framerange, query=True, text=True )
		self.chunksize = cmds.intSliderGrp( self.ui.chunksize, query=True, value=True )
		self.threads = cmds.intSliderGrp( self.ui.threads, query=True, value=True )
		self.checkoutput =  cmds.checkBoxGrp( self.ui.options, query=True, value1=True )
		self.quicktime =  cmds.checkBoxGrp( self.ui.options, query=True, value2=True )
		self.weight =  cmds.radioButtonGrp( self.ui.process, query=True, select=True )
		self.projectpath = cmds.workspace(q=True,fn=True)
				
		self.username = getpass.getuser()
		self.timestamp = int( time.time() )  
			
		if self.rendername.find( "[not set; using scene name]" ) >= 0:
			if not cmds.file( query=True, sceneName=True ):
				self.rendername = "MayaRender-%s" % self.username
			else:
				scenepath = cmds.file( query=True, sceneName=True )
				self.rendername = scenepath.split("/")[-1].split(".")[0]
				
		
		try:
			spooldir = "/mnt/muxfs/users/%s/spool" % self.username  # should be built from a template in cfg
			if not os.path.exists( spooldir ):
				os.makedirs( spooldir )
		except:
			print "Warning. Attempt to create spool directory %s failed" % spooldir
					
		filename = "maya-%s-%s.ma" % ( self.username, self.timestamp )
		filepath = os.path.join( spooldir, filename )
		
		try:
			cmds.file( rename=filepath )
			cmds.file( save=True, type='mayaAscii' )
		except:
			cmds.confirmDialog( title='Error', message='Error, unable to save scene to %s'%filepath)
		finally:
			cmds.file( rename=self.sceneInfo['SceneName'] )
		
		maya_args   = {  "type":"Maya", "threads":self.threads, "file":filepath, "layers":self.selectedLayers() }    
		render_args = { "range":self.framerange,  "chunksize":self.chunksize, "timestamp":self.timestamp, "name":self.rendername,  "user":self.username,
						"quicktime":self.quicktime, "weight":self.weight , "check":self.checkoutput, "title":self.jobname, "projectpath":self.projectpath }

		print render_args
		print maya_args
			
		launchRender( render_args, maya_args )  
		
	def selectedLayers( self ):
		return cmds.textScrollList( self.ui.renderlayers, query=True, selectItem=True )
		
def startRenderDialog():
	
	dialog = pyRenderDialog()
	dialog.show()

def launchRender( jobargs, cmdargs ):
		mayaRenderObj = tractor.Render( jobargs, cmdargs )
		mayaRenderObj.build()
		mayaRenderObj.spool()

def getSceneInfo():
	
	result = {}
	result['MayaVersion'] = mel.eval('getApplicationVersionAsFloat')
	result['SceneName'] = cmds.file( q=True, location=True )
	result['DatabaseDir'] = cmds.workspace( q=True, rd=True )
	return result

def getRenderableLayers( sceneinfo ):
	allLayers = cmds.listConnections( "renderLayerManager", t="renderLayer")
	renderableLayers = []
	
	if len(allLayers) > 1:
		for layer in allLayers:
			if cmds.getAttr( '%s.renderable'%layer ):
				renderableLayers.append( layer )
	
	return renderableLayers

def menu():
	gMainWindow =  mel.eval ('global string $gMainWindow; string $temp=$gMainWindow;' )
	
	cmds.menu( "Baseblack", label="Baseblack", parent=gMainWindow )
	cmds.menuItem( subMenu=True, label='Tractor' )
	cmds.menuItem( label="Render", command="import pySubmitMaya\npySubmitMaya.startRenderDialog()" )




	
