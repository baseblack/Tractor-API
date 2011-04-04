# stupidly simple render submission panel

import nuke
import getpass
import time
import tractor.glue.render as tractor

class submit_gui( object ):

    __renderName = None
    __frameRange = "1-100"
    __writePulldown = "input global custom"
    __threadPulldown = "1 2 3 4 5 6 7 8"
    __chunkPulldown = "None 50 20 10 5 2 1"
    __writeNodePulldown = ""
    __writeNodePath = None
    
    __proxyCheckbox = False
    __quietCheckbox = False
    __splitWriteNodesCheckbox = False
        

    def __init__( self, *argv, **kwargs ):
        self.writeNodes = {}
           
        allWriteNodes = [n for n in nuke.allNodes() if n.Class() in ('Write')]
        
        print allWriteNodes
        for node in allWriteNodes:
            nodename = node.fullName()
            nodefilepath = node.knob("file").value()
            self.writeNodes[nodename] = nodefilepath
                    
        self.__writeNodePulldown = " ".join( self.writeNodes.keys() )
        if self.writeNodes :
            self.__writeNodePath = self.writeNodes.values()[0]

        self.__drawPanel()

    def __drawPanel( self ):
                
        self.panel = nuke.Panel("Render")
        
        #self.panel.addEnumerationPulldown("Frame Range", self.__writePulldown)
        self.panel.addSingleLineInput( "Render Name", self.__renderName )
        self.panel.addSingleLineInput( "Frame Range", self.__frameRange )

        #self.panel.addEnumerationPulldown( "Write Node", self.__writeNodePulldown )
        #self.panel.addSingleLineInput( "Output Path", self.__writeNodePath )        


        self.panel.addEnumerationPulldown("Num Threads", self.__threadPulldown)
        self.panel.addEnumerationPulldown("Frames per Chunk", self.__chunkPulldown)
        
        self.panel.addBooleanCheckBox("Force Fullsize", self.__proxyCheckbox)
        self.panel.addBooleanCheckBox("Quiet Mode", self.__quietCheckbox)
        
        self.panel.addButton( "Cancel" )
        self.panel.addButton( "OK" )
        
        #self.panel.setWidth(600)
        
    def cancel( self ):
        pass
        
    def show( self ):
        result = self.panel.show()
        
        if result == 0:
            self.cancel()
        elif result ==1:
            self.render()
            
    def showModal( self ):
        self.panel.showModalDialog()
        
    def render( self ):
        
        frame_range  = self.panel.value("Frame Range")
        thread_count = self.panel.value("Num Threads")
        chunk_size     = self.panel.value("Frames per Chunk")
        force_fullsize   = self.panel.value("Force Fullsize")
        quiet_mode    = self.panel.value("Quiet Mode")
        render_name = self.panel.value("Render Name")
        
        if chunk_size == "None":
                chunk_size = 0

        username = getpass.getuser()
        timestamp = int( time.time() )        
        
        if render_name is None: 
            render_name = "Nuke Render for %s" % username
        
        filename = "/tmp/nuke-%s-%s-%s.nk" % ( frame_range, username, timestamp )
        
        try:
            nuke.scriptSave( filename )
            print filename
        except:
            nuke.message("ERR-001 Unable to save spool file")
            
        nuke_args   = {  "type":"Nuke", "threads":thread_count, "fullsize":force_fullsize, "quiet":quiet_mode, "file":filename, "nodes":self.writeNodes}    
        render_args = { "range":frame_range,  "chunksize":chunk_size, "timestamp":timestamp, "name":render_name,  "user":username,}
        
        print render_args
        print nuke_args
        
        rr = tractor.Render( render_args, nuke_args )
        rr.build()
        rr.spool()

