import maya.cmds as cmds
import os
import re
import ntpath
import posixpath

SceneDir = str(cmds.file(q=True, exn=True))


def buildScene(): #Detects what scene the user is in
    if(SceneDir.find("animation") != -1):
        print('Animation')
    elif(SceneDir.find("layout") != -1):
        print('Layout')
    elif(SceneDir.find("light") != -1):
        print('Lighting')
    else:
        print('Scene Not Identified')

def importSetAssets():



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

cmds.button(label='Build Current Scene', command='buildScene()')
cmds.separator(h=20)

cmds.showWindow('Scene_Builder')
