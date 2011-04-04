import sys
import os
import getpass
import time

import nuke
from nukescripts import pyQtAppUtils, utils
import tractor.glue.render as tractor

def initPyQtSubmitDialog( pyQtApp, appArgv=['pyQtSubmitDialog'] ):
	from PyQt4 import QtCore, QtGui, uic
	
	class pyQtSubmitDialog(object):
		def __init__(self):
			# Set up the user interface from Designer.
						
			self.ui = uic.loadUi( self.uipath() )
			self.ui.connect(self.ui.renderButton, QtCore.SIGNAL("clicked()"), self.render)
			self.ui.connect(self.ui.refreshButton, QtCore.SIGNAL("clicked()"), self.refresh)
			nuke.addOnCreate(self.onCreateCallback)
			nuke.addOnDestroy(pyQtThreadCleanupCallback, nodeClass='Root')

			self.setdefaults()

			self.ui.show()

		def uipath( self ):
			module = sys.modules[self.__module__] 
			modulepath = os.path.realpath( module.__file__ )
			moduledir = os.path.dirname( modulepath )
			
			relativeUIpath = "./pyQtSubmitDialog.ui"
			return os.path.join( moduledir, relativeUIpath )

		def setdefaults(self):
			self.ui.frameRange.setText( "1-100" )
			
			self.ui.renderName.setText("Default Render")
			self.ui.chunkComboBox.setCurrentIndex( 0 )
			self.ui.threadSpinBox.setValue( 4 )
			self.refresh()

		def onCreateCallback(self):
			n = nuke.thisNode()
			if n.Class() == "Write":
				n.setName(n.name())
				self.addItem(n)
				
		def refresh( self ):
			self.ui.treeWidget.clear()
			nodes = nuke.allNodes("Write")
			for n in nodes:
				n.setName(n.name())
				self.addItem(n)

		def addItem(self, n):
			item = QtGui.QTreeWidgetItem()
			item.setText(0, n['name'].value())
			self.ui.treeWidget.addTopLevelItem(item)
			
		def selectedWriteNodes( self ):
			
			selectedNodes = QtCore.QStringList()
			
			nodeCount = self.ui.treeWidget.topLevelItemCount()
			for i in range( nodeCount ):
				item = self.ui.treeWidget.topLevelItem(i)
				if self.ui.treeWidget.isItemSelected( item ):
					selectedNodes.append( str( item.text(0) ) )
			
			if len( selectedNodes ) == 0:
				nuke.message("You must select a write node. It's onerous I know but live with it.")
			
			return selectedNodes.join(",")

		def render(self):
			render_name = self.ui.renderName.text()
			frame_range = self.ui.frameRange.text()
			chunk_size = self.ui.chunkComboBox.currentText()
			force_fullsize = self.ui.fullsizeCheckbox.isChecked()
			quiet_mode = self.ui.quietCheckbox.isChecked()
			thread_count = self.ui.threadSpinBox.value()
			
			if chunk_size == "None": chunk_size = 0;
			
			self.username = getpass.getuser()
			self.timestamp = int( time.time() )        

			#username = "steve"
			#timestamp = "123445677"
			
			if render_name is None: 
				render_name = "Nuke Render for %s" % self.username

			try:
				spooldir = "/mnt/muxfs/users/%s/spool" % self.username  # should be built from a template in cfg
				exists = utils.executeInMainThreadWithResult( os.path.exists, ( spooldir, ) )
				if not exists:
					utils.executeInMainThreadWithResult( os.makedirs, ( spooldir, ) )
			except:
				print "Warning. Attempt to create spool directory failed"
		
			filename = "nuke-%s-%s.nk" % ( self.username, self.timestamp )
			filepath = os.path.join( spooldir, filename )
			
			try:
				utils.executeInMainThreadWithResult( nuke.scriptSave, (filepath,) )
				print filepath
			except:
				nuke.message("ERR-001 Unable to save spool file")

			nuke_args   = {  "type":"Nuke", "threads":thread_count, "fullsize":force_fullsize, "quiet":quiet_mode, "file":filepath, "nodes":self.selectedWriteNodes() }    
			render_args = { "range":frame_range,  "chunksize":chunk_size, "timestamp":self.timestamp, "name":render_name,  "user":self.username,}

			print render_args
			print nuke_args
			
			launchRender( render_args, nuke_args )  
			
			self.ui.close()	
				
	app = pyQtApp.getApplication(appArgv)
	dialog = pyQtSubmitDialog()
	app.exec_()

def launchRender( jobargs, cmdargs ):
		tr = tractor.Render( jobargs, cmdargs )
		tr.build()
		tr.spool()

def startQtRenderDialog():
	pyQtApp = pyQtAppUtils.pyQtAppHelper(start = True)
	pyQtApp.run(initPyQtSubmitDialog, (pyQtApp,))
	return pyQtApp

def pyQtThreadCleanupCallback():
	import threading
	from nukescripts import pyQtAppUtils
	
	for t in threading.enumerate():
		if(t.getName() == "Nuke_PyQt_Thread"):
			pyQtApp = pyQtAppUtils.pyQtAppHelper()
			pyQtApp.stop()
