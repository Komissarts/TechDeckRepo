import maya.cmds as cmds
import os
import re
import ntpath
import posixpath

SceneDir = str(cmds.file(q=True, exn=True))

def buildScene():
    print('button pressed')


#GUI
if cmds.window('Scene_Builder', exists = True):
    cmds.deleteUI('Scene_Builder')
cmds.window('Scene_Builder', resizeToFitChildren = True)
cmds.columnLayout(adjustableColumn = True, cal = "center", w=300)
cmds.separator(h=10)
cmds.text('SceneDirectory')
cmds.separator(h=10)
cmds.textField(tx = SceneDir)
cmds.separator(h=20)

cmds.text('Build New Scene')
department = cmds.radioButtonGrp(label='Select Department: ', labelArray3=['Layout', 'Animation', 'Lighting'], numberOfRadioButtons=3)
cmds.button(label='Build Scene', command='buildScene()')
cmds.separator(h=20)


cmds.showWindow('Scene_Builder')
