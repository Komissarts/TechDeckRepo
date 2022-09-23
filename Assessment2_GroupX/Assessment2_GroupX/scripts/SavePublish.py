def SavePublishWindow():
    
    if cmds.window('SavePublishWindow', exists = True):
        cmds.deleteUI('SavePublishWindow')
    
    cmds.window(width = 100)
    cmds.window('SavePublishWindow', resizeToFitChildren = True)
    
    cmds.columnLayout(adjustableColumn = True)
    
    cmds.text(label = "Project File Directory:",  align = "left")
    cmds.textField()
    
    cmds.separator(h = 10)
    cmds.text(label = "Selected object's name", align = "center", font = "boldLabelFont")
    cmds.text(label = "assetName", align = "center", font = "fixedWidthFont")
    cmds.separator(h = 10)
    
    cmds.text(label = "Asset Department Selection")
    cmds.button(label = "SetPiece", align = "center", enable = False)
    cmds.button(label = "Set", align = "center")
    cmds.button(label = "Props", align = "center")
    cmds.button(label = "Character", align = "center")
    
    cmds.text(label = "Current Department Selected", align = "center")
    cmds.text(label = "SetPiece", align = "center", font = "boldLabelFont")
    
    cmds.separator(h=10)
    cmds.button(label = "Save", align = "center")
    cmds.button(label = "Publish", align = "center")
    
    cmds.separator(h = 20)
    
    cmds.text("Sequence Number")
    seqTF = cmds.textField()
    cmds.text("Shot Number")
    shotTF = cmds.textField()
    
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label = "Sequence Department Selection")
    cmds.button(label = "Animation", align = "center", enable = False)
    cmds.button(label = "Layout", align = "center")
    cmds.button(label = "Lighting", align = "center")
    
    cmds.text(label = "Current Department Selected", align = "center")
    cmds.text(label = "Animation", align = "center", font = "boldLabelFont")
    
    cmds.separator(h=10)
    cmds.button(label = "Save", align = "center")
    cmds.button(label = "Publish", align = "center")
    #cmds.rowColumnLayout(column = 2)
    cmds.separator(h = 20)
    cmds.text(label = "File save as assetName_model_v001.mb", align = "center")

    cmds.showWindow('SavePublishWindow')
SavePublishWindow()