import maya.cmds as cmds
import maya.mel
import maya.utils as mu

class MayaLayer:
    def __init__(self):
        self.name=""
        self.camera=""
        self.renderer=""
        self.requiredPlugins=""
        self.IsActive=False
        self.seqStart=1
        self.seqEnd=100
        self.seqStep=1
        self.seqFileOffset=0
        self.imageWidth=100
        self.imageHeight=100
        self.imageFileName=""
        self.imageFramePadding=1
        self.imageDir=""
        self.imageExtension=""
        self.imagePreNumberLetter=""
        self.ImageSingleOutputFile=False
        self.channelName=""        
        self.maxChannels=0
        self.channelFileName=[]
        self.channelExtension=[]
        self.tempModifyExtension=False
        self.tempModifyByframe=1
        self.tempModifyStart=1
        self.tempImageFormat=1
        self.tempImfKeyPlugin=""
        self.tempImageExtension="unknown"
        self.tempImageFilePrefix="unknown"
        self.tempExtensionPadding=1
        self.tempVersionTag=""
        self.tempIsGI=False
        self.tempIsGI2=False
        self.tempGIFileName=""
        self.tempCamNames = []
        self.tempCamRenderable = []
        return


    def GetSceneFps(self):
        FpsName= cmds.currentUnit(query=True, time=True)
        if (FpsName=="game"):
            return 15.0
        elif (FpsName=="film"):
            return 24.0
        elif (FpsName=="pal"):
            return 25.0
        elif (FpsName=="ntsc"):
            return 30.0
        elif (FpsName=="show"):
            return 48.0
        elif (FpsName=="palf"):
            return 50.0
        elif (FpsName=="ntscf"):
            return 60.0
        elif (FpsName=="millisec"):
            return 1000.0
        elif (FpsName=="sec"):
            return 1.0
        elif (FpsName=="min"):
            return (1.0/60.0)
        elif (FpsName=="hour"):
            return (1.0/60.0/60.0)
        elif (FpsName=="2fps"):
            return 2.0
        elif (FpsName=="3fps"):
            return 3.0
        elif (FpsName=="4fps"):
            return 4.0
        elif (FpsName=="5fps"):
            return 5.0
        elif (FpsName=="6fps"):
            return 6.0
        elif (FpsName=="8fps"):
            return 8.0
        elif (FpsName=="10fps"):
            return 10.0
        elif (FpsName=="12fps"):
            return 12.0
        elif (FpsName=="16fps"):
            return 16.0
        elif (FpsName=="20fps"):
            return 20.0
        elif (FpsName=="40fps"):
            return 40.0
        elif (FpsName=="75fps"):
            return 75.0
        elif (FpsName=="80fps"):
            return 80.0
        elif (FpsName=="100fps"):
            return 100.0
        elif (FpsName=="120fps"):
            return 120.0
        elif (FpsName=="125fps"):
            return 125.0
        elif (FpsName=="150fps"):
            return 150.0
        elif (FpsName=="200fps"):
            return 200.0
        elif (FpsName=="240fps"):
            return 240.0
        elif (FpsName=="250fps"):
            return 250.0
        elif (FpsName=="300fps"):
            return 300.0
        elif (FpsName=="375fps"):
            return 375.0
        elif (FpsName=="400fps"):
            return 400.0
        elif (FpsName=="500fps"):
            return 500.0
        elif (FpsName=="600fps"):
            return 600.0
        elif (FpsName=="750fps"):
            return 750.0
        elif (FpsName=="1200fps"):
            return 1200.0
        elif (FpsName=="1500fps"):
            return 1500.0
        elif (FpsName=="2000fps"):
            return 2000.0
        elif (FpsName=="3000fps"):
            return 3000.0
        elif (FpsName=="6000fps"):
            return 6000.0
        else:
            return 25.0
            
    def CalcImageExtension(self):
        if (self.renderer=="renderMan"):
            rmanImages = maya.mel.eval('rman getPrefAsArray ImageFormatQuantizationTable;')
            for img in range(1, len(rmanImages)-1):
                if (rmanImages[img]==self.tempImfKeyPlugin):
                    self.tempImageExtension= rmanImages[img-1]
                    if (self.tempImageExtension.find("(")>=0):
                        self.tempImageExtension=self.tempImageExtension[self.tempImageExtension.find("(")+1:] 
                        if (self.tempImageExtension.find(")")>=0):
                            self.tempImageExtension=self.tempImageExtension[:self.tempImageExtension.find("(")]
                            return
            self.tempImageExtension=".unknown"
            return
        
        #MRay, Maya Software:
        if (self.tempImageFormat== 60):
            self.tempImageExtension="swf"
        elif (self.tempImageFormat== 61):
            self.tempImageExtension="ai"
        elif (self.tempImageFormat== 62):
            self.tempImageExtension="svg"
        elif (self.tempImageFormat== 63):
            self.tempImageExtension="swft"
        elif (self.tempImageFormat== 50):
            mayaimfPlugInExt = maya.mel.eval('$rrTempimfPlugInExt = $imfPlugInExt;')
            mayaimfPlugInKey = maya.mel.eval('$rrTempimfPlugInKey = $imfPlugInKey;')
            for i in range(0, len(mayaimfPlugInKey)):
                if (mayaimfPlugInKey[i]==self.tempImfKeyPlugin):
                    self.tempImageExtension=mayaimfPlugInKey[i]
        elif (self.tempImageFormat== 51):
            self.tempImageExtension=self.tempImfKeyPlugin
        else:
            try:          
                mayaImgExt = maya.mel.eval('$rrTempimgExt = $imgExt;')
                if (len(mayaImgExt)==0):
                    maya.mel.eval('createImageFormats()')
                    mayaImgExt = maya.mel.eval('$rrTempimgExt2 = $imgExt;')
            except:
                maya.mel.eval('createImageFormats()')
                mayaImgExt = maya.mel.eval('$rrTempimgExt2 = $imgExt;')
            self.tempImageExtension = mayaImgExt[self.tempImageFormat]
        if (self.renderer=="mentalRay"):
            if (self.tempImageExtension=="sgi"):
                self.tempImageExtension="rgb"
            if (self.tempImageExtension=="tifu"):
                self.tempImageExtension="tif"
            if (self.tempImageExtension=="qntntsc"):
                self.tempImageExtension="yuv"
            if (self.tempImageExtension=="qntpal"):
                self.tempImageExtension="yuv"
        if (self.tempImageExtension=="jpeg"):
            self.tempImageExtension="jpg"
             
            
    # gather all information from a layer
    def getLayerSettings(self,Layer,DatabaseDir,SceneName,MayaVersion,isLayerRendering):
        self.tempVersionTag = cmds.getAttr('defaultRenderGlobals.renderVersion')
        if ((self.tempVersionTag==None) or (len(self.tempVersionTag)==0)):
            self.tempVersionTag=""            
        CurrentLayer=cmds.editRenderLayerGlobals( query=True, currentRenderLayer=True )
        LayerOverrides=cmds.listConnections( Layer+".adjustments", p=True, c=True)
        LayerOverridesMaster=cmds.listConnections( "defaultRenderLayer.adjustments", p=True, c=True)

        self.renderer= cmds.getAttr('defaultRenderGlobals.currentRenderer')
        if (CurrentLayer!=Layer):
            if ( (not (LayerOverridesMaster==None) ) and (len(LayerOverridesMaster)>1)):
                for o in range(0, len(LayerOverridesMaster) /2  ):
                    OWhat=LayerOverridesMaster[o*2+1]
                    LayerOverridesMaster[o*2]=LayerOverridesMaster[o*2].replace(".plug",".value")
                    OValue=cmds.getAttr(LayerOverridesMaster[o*2])
                    if (OWhat=="defaultRenderGlobals.currentRenderer"):
                        self.renderer= OValue
            if ( (not (LayerOverrides==None) ) and (len(LayerOverrides)>1)):
                for o in range(0, len(LayerOverrides) /2  ):
                    OWhat=LayerOverrides[o*2+1]
                    LayerOverrides[o*2]=LayerOverrides[o*2].replace(".plug",".value")
                    OValue=cmds.getAttr(LayerOverrides[o*2])
                    if (OWhat=="defaultRenderGlobals.currentRenderer"):
                        self.renderer= OValue
        if (self.renderer!="mayaSoftware"):
            self.requiredPlugins=self.renderer+";"

        #VRAY only:
        if (self.renderer=="vray"):
            vrayVersion=cmds.pluginInfo( 'vrayformaya', query=True, version=True )
            isVRaySP=(vrayVersion.find("SP")>=0)
            self.imageWidth= int(cmds.getAttr('vraySettings.width'))
            self.imageHeight= int(cmds.getAttr('vraySettings.height'))
            self.imageFramePadding=cmds.getAttr('vraySettings.fileNamePadding')
            self.imageFileName=cmds.getAttr('vraySettings.fileNamePrefix')
            self.imageExtension=cmds.getAttr('vraySettings.imageFormatStr')
            self.imagePreNumberLetter=cmds.getAttr('vraySettings.fileNameRenderElementSeparator')      
            self.camera=cmds.getAttr('vraySettings.batchCamera')
            if (isVRaySP):
                print("VRay SP1")
                isAnimation= cmds.getAttr('defaultRenderGlobals.animation')
                self.seqStart= int(cmds.getAttr('defaultRenderGlobals.startFrame'))
                self.seqEnd= int(cmds.getAttr('defaultRenderGlobals.endFrame'))
                self.seqStep= int(cmds.getAttr('defaultRenderGlobals.byFrameStep'))
            else:
                print("VRay")
                isAnimation= cmds.getAttr('vraySettings.animation')
                self.seqStart= int(cmds.getAttr('vraySettings.startFrame'))
                self.seqEnd= int(cmds.getAttr('vraySettings.endFrame'))
                self.seqStep= int(cmds.getAttr('vraySettings.frameStep'))
            self.tempIsGI= cmds.getAttr('vraySettings.giOn')
            self.tempIsGI2= ( (cmds.getAttr('vraySettings.imap_mode')==6) or (cmds.getAttr('vraySettings.imap_mode')==1))
            self.tempGIFileName=cmds.getAttr('vraySettings.imap_autoSaveFile')
            
            self.ImageSingleOutputFile=False
            if (isAnimation!=1):
                self.ImageSingleOutputFile=True
                print "Still frames not allowed!\n Please use a sequence with one frame.\n Layer: "+Layer+"\n"
                return False  
            if ((self.imageFileName==None) or (len(self.imageFileName)==0)):
                self.imageFileName=SceneName
                self.imageFileName=self.imageFileName.replace("\\","/")
                if (self.imageFileName.find("/")>=0):
                    splitted=self.imageFileName.split("/")
                    self.imageFileName=splitted[len(splitted)-1]
                if (self.imageFileName.find(".")>=0):
                    splitted=self.imageFileName.split(".")
                    self.imageFileName=splitted[0]

            if (CurrentLayer!=Layer):
                if ( (not (LayerOverridesMaster==None) ) and (len(LayerOverridesMaster)>1)):
                    for o in range(0, len(LayerOverridesMaster) /2  ):
                        OWhat=LayerOverridesMaster[o*2+1]
                        LayerOverridesMaster[o*2]=LayerOverridesMaster[o*2].replace(".plug",".value")
                        OValue=cmds.getAttr(LayerOverridesMaster[o*2])
                        
                        if (OWhat=="vraySettings.width"):
                            self.imageWidth= int(OValue)
                        elif (OWhat=="vraySettings.height"):
                            self.imageHeight= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.startFrame")):
                            self.seqStart= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.endFrame")):
                            self.seqEnd= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.byFrameStep")):
                            self.seqStep= int(OValue)
                        elif (OWhat=="vraySettings.startFrame"):
                            self.seqStart= int(OValue)
                        elif (OWhat=="vraySettings.endFrame"):
                            self.seqEnd= int(OValue)
                        elif (OWhat=="vraySettings.frameStep"):
                            self.seqStep= int(OValue)
                        elif (OWhat=="vraySettings.fileNamePadding"):
                            self.imageFramePadding= int(OValue)
                        elif (OWhat=="vraySettings.fileNamePrefix"):
                            self.imageFileName=OValue
                        elif (OWhat=="vraySettings.imageFormatStr"):
                            self.imageExtension=OValue
                        elif (OWhat=="vraySettings.fileNameRenderElementSeparator"):
                            self.imagePreNumberLetter=OValue
                        elif (OWhat=="vraySettings.batchCamera"):
                            self.camera=OValue
                        elif (OWhat=="vraySettings.giOn"):
                            self.tempIsGI=OValue
                        elif (OWhat=="vraySettings.imap_mode"):
                            self.tempIsGI2=((int(OValue)==6) or (int(OValue)==1))
                        elif (OWhat=="vraySettings.imap_autoSaveFile"):
                            self.tempGIFileName=OValue
                if ( (not (LayerOverrides==None) ) and (len(LayerOverrides)>1)):
                    for o in range(0, len(LayerOverrides) /2  ):
                        OWhat=LayerOverrides[o*2+1]
                        LayerOverrides[o*2]=LayerOverrides[o*2].replace(".plug",".value")
                        OValue=cmds.getAttr(LayerOverrides[o*2])
                        
                        if (OWhat=="vraySettings.width"):
                            self.imageWidth= int(OValue)
                        elif (OWhat=="vraySettings.height"):
                            self.imageHeight= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.startFrame")):
                            self.seqStart= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.endFrame")):
                            self.seqEnd= int(OValue)
                        elif (isVRaySP and (OWhat=="defaultRenderGlobals.byFrameStep")):
                            self.seqStep= int(OValue)
                        elif (OWhat=="vraySettings.startFrame"):
                            self.seqStart= int(OValue)
                        elif (OWhat=="vraySettings.endFrame"):
                            self.seqEnd= int(OValue)
                        elif (OWhat=="vraySettings.frameStep"):
                            self.seqStep= int(OValue)
                        elif (OWhat=="vraySettings.fileNamePadding"):
                            self.imageFramePadding= int(OValue)
                        elif (OWhat=="vraySettings.fileNamePrefix"):
                            self.imageFileName=OValue
                        elif (OWhat=="vraySettings.imageFormatStr"):
                            self.imageExtension=OValue
                        elif (OWhat=="vraySettings.fileNameRenderElementSeparator"):
                            self.imagePreNumberLetter=OValue
                        elif (OWhat=="vraySettings.batchCamera"):
                            self.camera=OValue
                        elif (OWhat=="vraySettings.giOn"):
                            self.tempIsGI=OValue
                        elif (OWhat=="vraySettings.imap_mode"):
                            self.tempIsGI2=((int(OValue)==6) or (int(OValue)==1))
                        elif (OWhat=="vraySettings.imap_autoSaveFile"):
                            self.tempGIFileName=OValue
            
            if ((self.imageExtension==None) or (len(self.imageExtension)==0)):
                self.imageExtension="png"
            self.imageExtension= "."+ self.imageExtension
            if ((self.imageExtension==".exr (multichannel)")):
                self.imageExtension=".exr"
                self.imagePreNumberLetter=""
            if ((self.camera==None) or (len(self.camera)==0)):
                self.camera=""            
            if ((self.tempIsGI) and (self.tempIsGI2)):
                self.imageFileName=self.tempGIFileName
                self.imageExtension=""
                self.imagePreNumberLetter=""
                self.renderer="vray_prepass"
                if (self.imageFileName.find(".vrmap")>=0):
                    splitted=self.imageFileName.split(".vrmap")
                    self.imageFileName=splitted[0]
                    self.imageExtension=".vrmap"
                

            self.imageFileName= self.imageFileName + self.imagePreNumberLetter
            self.imageFileName=self.imageFileName.replace("%/l","<Layer>/")
            self.imageFileName=self.imageFileName.replace("%l","<Layer>")
            self.imageFileName=self.imageFileName.replace("<RenderLayer>","<Layer>")        
            self.imageFileName=self.imageFileName.replace("<RenderPass>","<Channel>")        
            self.imageFileName=self.imageFileName.replace("%/c","<Camera>/")
            self.imageFileName=self.imageFileName.replace("%c","<Camera>")
            self.imageFileName=self.imageFileName.replace("%/s","<SceneFile>/")
            self.imageFileName=self.imageFileName.replace("%s","<SceneFile>")
            self.imageFileName=self.imageFileName.replace("<Scene>","<SceneFile>")
            self.imageFileName=self.imageFileName.replace("<Channel>","")
            self.imageFileName=self.imageFileName.replace("%e",self.tempImageExtension)
            self.imageFileName=self.imageFileName.replace("<Extension>",self.tempImageExtension)
            self.imageFileName=self.imageFileName.replace("<Version>",self.tempVersionTag)
            if (isLayerRendering and (self.imageFileName.find("<Layer>")<0)):
                self.imageFileName="<Layer>/"+self.imageFileName
            

            if (self.renderer=="vray_prepass"):
                self.ImageDir=""
            else:
                self.ImageDir= cmds.workspace(fre="images")
                isRelative=True
                if (len(self.ImageDir)>1):                
                    self.ImageDir=self.ImageDir.replace("\\","/")
                    if (self.ImageDir[0]=="/"):
                        isRelative=False
                    if (self.ImageDir[1]==":"):
                        isRelative=False
                if (isRelative):
                    self.ImageDir=DatabaseDir+self.ImageDir
                    self.ImageDir+="/"

            return True
            #"VRay Only" returned
        

        #MentalRay, Maya software, hardware renderer, Renderman:
        attrNameImfkey="defaultRenderGlobals.imfPluginKey";
        if (self.renderer=="renderMan"):
            attrNameImfkey="rmanFinalOutputGlobals0.rman__riopt__Display_type";
            
        self.imageWidth= int(cmds.getAttr('defaultResolution.width'))
        self.imageHeight= int(cmds.getAttr('defaultResolution.height'))
        self.seqStart= int(cmds.getAttr('defaultRenderGlobals.startFrame'))
        self.seqEnd= int(cmds.getAttr('defaultRenderGlobals.endFrame'))
        self.seqStep= int(cmds.getAttr('defaultRenderGlobals.byFrameStep'))
        self.tempModifyExtension=(cmds.getAttr('defaultRenderGlobals.modifyExtension')==True)
        self.tempModifyStart=int(cmds.getAttr('defaultRenderGlobals.startExtension'))
        self.tempModifyByframe=int(cmds.getAttr('defaultRenderGlobals.byExtension'))
        self.tempImageFormat=int(cmds.getAttr('defaultRenderGlobals.imageFormat'))        
        self.tempImfKeyPlugin=cmds.getAttr(attrNameImfkey)
        self.tempImageFilePrefix=cmds.getAttr('defaultRenderGlobals.imageFilePrefix')
        self.tempExtensionPadding=cmds.getAttr('defaultRenderGlobals.extensionPadding')
        isAnimation= cmds.getAttr('defaultRenderGlobals.animation')
        if (isAnimation!=1):
            self.ImageSingleOutputFile=True
            return False        

        cameraList=cmds.ls(ca=True)
        for cam in cameraList:
            self.tempCamNames.append(cam);
            if (cmds.getAttr(cam+'.renderable')):
                self.tempCamRenderable.append(True)
            else:
                self.tempCamRenderable.append(False)
        self.ImageSingleOutputFile=False
        if (CurrentLayer!=Layer):
            if ( (not (LayerOverridesMaster==None) ) and (len(LayerOverridesMaster)>1)):
                for o in range(0, len(LayerOverridesMaster) /2  ):
                    OWhat=LayerOverridesMaster[o*2+1]
                    LayerOverridesMaster[o*2]=LayerOverridesMaster[o*2].replace(".plug",".value")
                    OValue=cmds.getAttr(LayerOverridesMaster[o*2])

                    for c in range(0, len(self.tempCamNames)):
                        if (self.tempCamNames[c]+'.renderable'== OWhat):
                            if (OValue):
                                self.tempCamRenderable[c]=True
                            else:
                                self.tempCamRenderable[c]=False
                    if (OWhat=="defaultResolution.width"):
                        self.imageWidth= int(OValue)
                    elif (OWhat=="defaultResolution.height"):
                        self.imageHeight= int(OValue)
                    elif (OWhat=="defaultRenderGlobals.startFrame"):
                        self.seqStart= int(OValue* self.GetSceneFps() +0.001 )
                    elif (OWhat=="defaultRenderGlobals.endFrame"):
                        self.seqEnd= int(OValue* self.GetSceneFps() +0.001 )
                    elif (OWhat=="defaultRenderGlobals.byFrameStep"):
                        self.seqStep= int(OValue* self.GetSceneFps() +0.001)
                    elif (OWhat=="defaultRenderGlobals.modifyExtension"):
                        self.tempModifyExtension=(OValue==True)
                    elif (OWhat=="defaultRenderGlobals.startExtension"):
                        self.tempModifyStart=int(OValue)
                    elif (OWhat=="defaultRenderGlobals.byExtension"):
                        self.tempModifyByframe=int(OValue)
                    elif (OWhat=="defaultRenderGlobals.imageFormat"):
                        self.tempImageFormat=int(OValue)
                    elif (OWhat==attrNameImfkey):
                        self.tempImfKeyPlugin=OValue
                    elif (OWhat=="defaultRenderGlobals.imageFilePrefix"):
                        self.tempImageFilePrefix=OValue
                    elif (OWhat=="defaultRenderGlobals.extensionPadding"):
                        self.tempExtensionPadding=OValue
            if ( (not (LayerOverrides==None) ) and (len(LayerOverrides)>1)):
                for o in range(0, len(LayerOverrides) /2  ):
                    OWhat=LayerOverrides[o*2+1]
                    LayerOverrides[o*2]=LayerOverrides[o*2].replace(".plug",".value")
                    OValue=cmds.getAttr(LayerOverrides[o*2])

                    for c in range(0, len(self.tempCamNames)):
                        if (self.tempCamNames[c]+'.renderable'== OWhat):
                            if (OValue):
                                self.tempCamRenderable[c]=True
                            else:
                                self.tempCamRenderable[c]=False
                    if (OWhat=="defaultResolution.width"):
                        self.imageWidth= int(OValue)
                    elif (OWhat=="defaultResolution.height"):
                        self.imageHeight= int(OValue)
                    elif (OWhat=="defaultRenderGlobals.startFrame"):
                        self.seqStart= int(OValue* self.GetSceneFps() +0.001)
                    elif (OWhat=="defaultRenderGlobals.endFrame"):
                        self.seqEnd= int(OValue* self.GetSceneFps() +0.001)
                    elif (OWhat=="defaultRenderGlobals.byFrameStep"):
                        self.seqStep= int(OValue* self.GetSceneFps() +0.001)
                    elif (OWhat=="defaultRenderGlobals.modifyExtension"):
                        self.tempModifyExtension=(OValue==True)
                    elif (OWhat=="defaultRenderGlobals.startExtension"):
                        self.tempModifyStart=int(OValue)
                    elif (OWhat=="defaultRenderGlobals.byExtension"):
                        self.tempModifyByframe=int(OValue)
                    elif (OWhat=="defaultRenderGlobals.imageFormat"):
                        self.tempImageFormat=int(OValue)
                    elif (OWhat==attrNameImfkey):
                        self.tempImfKeyPlugin=OValue
                    elif (OWhat=="defaultRenderGlobals.imageFilePrefix"):
                        self.tempImageFilePrefix=OValue
                    elif (OWhat=="defaultRenderGlobals.extensionPadding"):
                        self.tempExtensionPadding=OValue

        nbRenderableCams=0
        for c in range(0, len(self.tempCamRenderable)):
            if (self.tempCamRenderable[c]):
                nbRenderableCams=nbRenderableCams+1
                transformNode = cmds.listRelatives(self.tempCamNames[c],parent=True)
                transformNode=transformNode[0]
                self.camera=transformNode

        self.CalcImageExtension()

        if ( self.tempModifyExtension):
            self.seqFileOffset=self.tempModifyStart
            if (self.tempModifyByframe!="1"):
                rrWriteLog("No 'By Frame' renumbering allowed!\n Layer: "+Layer+"\n")
                return False
            else:
                self.seqFileOffset=0
        if (not self.getImageOut(DatabaseDir,MayaVersion,SceneName)):
            return False

        if (nbRenderableCams>1):
            for c in range(0, len(self.tempCamRenderable)):
                if (self.tempCamRenderable[c]):
                    nbRenderableCams=nbRenderableCams+1
                    transformNode = cmds.listRelatives(self.tempCamNames[c],parent=True)
                    transformNode=transformNode[0]
                    if (self.camera!=transformNode):
                        self.channelFileName.append(self.imageFileName.replace('<Camera>',transformNode))
                        self.channelExtension.append(self.imageExtension)
                        self.maxChannels +=1
            self.camera=self.camera + " ClearAtSubmit"

        if (self.renderer == 'mentalRay') and (MayaVersion>=2009.0):
            self.addChannelsToLayer()

        return True



    #add MRay Render Passes to layer (for information only)
    def addChannelsToLayer(self):
        name = self.name
        if self.name == 'masterLayer':
            name = 'defaultRenderLayer'
        passes = cmds.listConnections(name+'.renderPass')
        if passes == None or len(passes) == 0:
            return
        for p in passes:
            if ((cmds.nodeType(p)=="renderPass") and (cmds.getAttr(p+'.renderable') == 1)):
                self.channelFileName.append(self.imageFileName.replace('<Channel>',p))
                self.channelExtension.append(self.imageExtension)
                self.maxChannels +=1


    #calculate image name from layer/render settings for Maya 2009+:
    def getImageOut2009(self):
        maya.mel.eval('renderSettings -fin -lyr "'+self.name+'";') # workaround for batch mode to load command
        RenderOut=cmds.renderSettings(ign=True,lyr=self.name)        
        RenderOut=RenderOut[0]
        RenderOut=RenderOut.replace("\\","/")
        FNsplitter=""
        if (RenderOut.find("%0n")>=0):
            FNsplitter="%0n"
            self.imageFramePadding=1
        if (RenderOut.find("%1n")>=0):
            FNsplitter="%1n"
            self.imageFramePadding=1
        if (RenderOut.find("%2n")>=0):
            FNsplitter="%2n"
            self.imageFramePadding=2
        if (RenderOut.find("%3n")>=0):
            FNsplitter="%3n"
            self.imageFramePadding=3
        if (RenderOut.find("%4n")>=0):
            FNsplitter="%4n"
            self.imageFramePadding=4
        if (RenderOut.find("%5n")>=0):
            FNsplitter="%5n"
            self.imageFramePadding=5
        if (RenderOut.find("%6n")>=0):
            FNsplitter="%6n"
            self.imageFramePadding=6
        if (RenderOut.find("%7n")>=0):
            FNsplitter="%7n"
            self.imageFramePadding=7
        if (RenderOut.find("%8n")>=0):
            FNsplitter="%8n"
            self.imageFramePadding=8
        if (RenderOut.find("%9n")>=0):
            FNsplitter="%9n"
            self.imageFramePadding=9
            
        if (len(FNsplitter)>0):
            Splitted=RenderOut.split(FNsplitter,1)
            self.imageFileName=Splitted[0]
            self.imageExtension=Splitted[1]
            if ((self.renderer=="renderMan") and (self.imagePreNumberLetter=="_")):
                if (self.name=="masterLayer"):
                    self.imageFileName+="__"
                else:
                    self.imageFileName+="_"
        else:
            self.imageFileName=RenderOut
            self.imageExtension=""

        self.imageFileName=self.imageFileName.replace("%/l","<Layer>/")
        self.imageFileName=self.imageFileName.replace("%l","<Layer>")
        self.imageFileName=self.imageFileName.replace("<RenderLayer>","<Layer>")        
        self.imageFileName=self.imageFileName.replace("%/c","<Camera>/")
        self.imageFileName=self.imageFileName.replace("%c","<Camera>")
        self.imageFileName=self.imageFileName.replace("%/s","<SceneFile>/")
        self.imageFileName=self.imageFileName.replace("%s","<SceneFile>")
        self.imageFileName=self.imageFileName.replace("<Scene>","<SceneFile>")
        self.imageFileName=self.imageFileName.replace("<RenderPass>","<Channel>")        
        self.imageFileName=self.imageFileName.replace("<Version>",self.tempVersionTag)

        if ((self.name=="masterLayer") and (self.renderer=="renderMan")):
            self.imageFileName=self.imageFileName.replace("<Layer>","")
        self.imageFileName=self.imageFileName.replace("//","/")
                
        if (self.imageFileName.find("<Channel>")>=0):
            if (self.renderer!="mentalRay"):
                self.imageFileName=self.imageFileName.replace("<Channel>","")
            else:
                self.channelName="MasterBeauty"
        self.imageFileName=self.imageFileName.replace("%e",self.tempImageExtension)
        self.imageExtension=self.imageExtension.replace("%e",self.tempImageExtension)
        self.imageFileName=self.imageFileName.replace("<Extension>",self.tempImageExtension)
        self.imageExtension=self.imageExtension.replace("<Extension>",self.tempImageExtension)

        
    #calculate image name from layer/render settings for Maya 8.5:
    def getImageOut85(self,SceneName):
        ImageNoExtension= cmds.getAttr('defaultRenderGlobals.outFormatControl')
        ImageperiodInExt= cmds.getAttr('defaultRenderGlobals.periodInExt')
        ImageputFrameBeforeExt= cmds.getAttr('defaultRenderGlobals.putFrameBeforeExt')
        self.imageFramePadding=self.tempExtensionPadding
        self.imageExtension=""
        if ((self.tempImageFilePrefix==None) or (len(self.tempImageFilePrefix)==0)):
            self.tempImageFilePrefix=SceneName
            self.tempImageFilePrefix=self.tempImageFilePrefix.replace("\\","/")
            if (self.tempImageFilePrefix.find("/")>=0):
                splitted=self.tempImageFilePrefix.split("/")
                self.tempImageFilePrefix=splitted[len(splitted)-1]
            if (self.tempImageFilePrefix.find(".")>=0):
                splitted=self.tempImageFilePrefix.split(".")
                self.tempImageFilePrefix=splitted[0]
        if (ImageperiodInExt==0):
            self.imagePreNumberLetter=""
        elif (ImageperiodInExt==1):
            self.imagePreNumberLetter="."
        elif (ImageperiodInExt==2):
            self.imagePreNumberLetter="_"
        
        if (not self.ImageSingleOutputFile):
            if (ImageNoExtension):
                self.imageFileName=self.tempImageFilePrefix
            else:
                self.imageFileName=self.tempImageFilePrefix+"."+self.tempImageExtension
        elif (ImageNoExtension):
            self.imageFileName=self.tempImageFilePrefix+"."
        elif (ImageperiodInExt==0):
            self.imageFileName=self.tempImageFilePrefix
            self.imageExtension="."+self.tempImageExtension
        elif (ImageperiodInExt==2):
            self.imageFileName=self.tempImageFilePrefix+"_"
            self.imageExtension="."+self.tempImageExtension
        elif (ImageputFrameBeforeExt):
            self.imageFileName=self.tempImageFilePrefix+"."
            self.imageExtension="."+self.tempImageExtension
        else:
            self.imageFileName=self.tempImageFilePrefix+"."
            self.imageExtension="."+self.tempImageExtension
            rrWriteLog("'name.ext.#' not supported!\n Layer: "+Layer+"\n")
            return False

        self.imageFileName=self.imageFileName.replace("<Version>",self.tempVersionTag)
        RenderLayer=cmds.listConnections( "renderLayerManager", t="renderLayer")

        return True

    
    #prepare image name from layer/render settings:    
    def getImageOut(self,DatabaseDir,MayaVersion,SceneName):
        ImageperiodInExt= cmds.getAttr('defaultRenderGlobals.periodInExt')
        if (ImageperiodInExt==0):
            self.imagePreNumberLetter=""
        elif (ImageperiodInExt==1):
            self.imagePreNumberLetter="."
        elif (ImageperiodInExt==2):
            self.imagePreNumberLetter="_"

        self.ImageDir= cmds.workspace(fre="images")
        isRelative=True
        if (len(self.ImageDir)>1):                
            self.ImageDir=self.ImageDir.replace("\\","/")
            if (self.ImageDir[0]=="/"):
                isRelative=False
            if (self.ImageDir[1]==":"):
                isRelative=False
        if (isRelative):
            self.ImageDir=DatabaseDir+self.ImageDir
            self.ImageDir+="/"
        self.imageFramePadding=0
        if (MayaVersion>=2009.0):
            self.getImageOut2009()
            return True
        else:
            return self.getImageOut85(SceneName)



class SceneInfo:
    def __init__(self):
        self.MayaVersion=""
        self.SceneName=""
        self.DatabaseDir=""
            
    def getSceneInfo(self):
        self.DatabaseDir=cmds.workspace( q=True, rd=True )
        self.SceneName=cmds.file( q=True, location=True )
        self.MayaVersion=maya.mel.eval('getApplicationVersionAsFloat')


def getAllLayers( sceneInfo ):
	"""mercillisuly ripped from royalrender"""
	
	renderLayers = []	#returnable
	
	allLayers = cmds.listConnections( "renderLayerManager", t="renderLayer")
	print allLayers
	
	layerBasedRendering = ( len( allLayers ) > 1 )
	
	#masterlayer information
	masterLayer = utils.MayaLayer()
	masterLayer.name = "masterlayer"
	masterLayer.isActive = (cmds.getAttr('defaultRenderLayer.renderable')==True)
	
	if not masterLayer.getLayerSettings( "defaultRenderLayer", sceneInfo.DatabaseDir, sceneInfo.SceneName, sceneInfo.MayaVersion, layerBasedRendering ) :
		print "master blah"
		return 
	
	renderLayers.append( masterLayer )
	
	if len(renderLayers) > 1:
		for layer in renderLayers:
			if layer != "defaultRenderLayer":
				Layer = utils.MayaLayer()
				Layer.name = layer
				Layer.isActive = cmds.getAttr( '%s.renderable'%layer )
				if not Layer.getLayerSettings( layer, sceneInfo.DatabaseDir, sceneInfo.SceneName, sceneInfo.MayaVersion, layerBasedRendering ) :
					print "layer foo"
					return
				
				renderLayers.append(Layer)
				
	if masterLayer.imageFileName.find("<Layer>") == -1:
		masterLayer.name = ""
	
	return renderLayers
	