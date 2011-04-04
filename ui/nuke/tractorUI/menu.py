import nuke
import simpleSubmitNuke
import pyQtSubmitNuke


menubar = nuke.menu("Nuke")
m = menubar.addMenu("Baseblack")

m.addCommand("Tractor/Simple", "dialog=simpleSubmitNuke.submit_gui(); dialog.show()", icon="BB_icon.png")
m.addCommand("Tractor/Complete", "pyQtSubmitNuke.startQtRenderDialog()", icon="BB_icon.png")

toolbar = nuke.toolbar("Nodes")
bb = toolbar.addMenu("Baseblack", "BB_icon.png")

bb.addCommand("Tractor/Simple", "dialog=simpleSubmitNuke.submit_gui(); dialog.show()", icon="BB_icon.png")
bb.addCommand("Tractor/Complete", "pyQtSubmitNuke.startQtRenderDialog()", icon="BB_icon.png")

