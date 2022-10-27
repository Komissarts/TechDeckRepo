import maya.cmds as mc
import os
import ntpath
import json
import posixpath

#Gets Relative File path of model 
SceneDir = str(mc.file(q=True, exn=True))

if(SceneDir.find("surfacing") != -1):
    isCurrentlyInLighting = False
elif(SceneDir.find("light") != -1):
    isCurrentlyInLighting = True
    
if(os.name == 'nt'):
    isRunningWindows = True


if(isCurrentlyInLighting == False):
    ShaderPUB_Dir = SceneDir.replace("wip", "publish")
    ShaderDirArray=[]
    for i in ShaderPUB_Dir.split('/'):
        ShaderDirArray.append(i)
    FileNameArray=[]
    for i in ShaderDirArray[-1].split('.'):
        FileNameArray.append(i)
    BaseSurfacingName = FileNameArray[0] + ".v"
    
    ShaderDirArray.remove(ShaderDirArray[-1])
    
    ShaderPUB_Dir = '/'.join(ShaderDirArray) + "/" 


elif(isCurrentlyInLighting == True):
    #LightPUB_Dir = SceneDir.replace("model/source", "surfacing")
    print("Currently In A Lighting Scene")


def PublishShaders():
    #mc.select(cl = True)
    selected = mc.ls(selection = True)
    ShadersToExport = []
    MeshDataToExport = []
    MeshMaterials={}
    
    if(len(selected) == 0):
        print("No Meshes Selected - Exporting All Shaders")
        
        selected = mc.ls('mRef_*')
        mc.select(selected)
        
    else:
        print("Meshes Selected: Exporting Shaders")
        
    if(not mc.listRelatives(selected[0], s=True)):
        print("Selected Group or Transform, using children")
        selected = mc.listRelatives(selected[0], c=True)
    
    for i in range(len(selected)):
        selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
        selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
        selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
        
        #adds the mesh and its material to a json Dict
        MeshMaterials[selectedMesh +":"+ selectedMat] = {"AttachedMaterial": selectedMat }
        
        ShadersToExport.append(selectedMat)
    mc.select(ShadersToExport)
    print("Shaders Exported: "+str(ShadersToExport))
        
    fileIncrementer = 1
    while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
        fileIncrementer += 1

    # Writing to .json File
    json_object = json.dumps(MeshMaterials, indent = 4)
    with open(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".json", "w") as outfile:
        outfile.write(json_object)
    
    mc.file(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb", force=True, op="v=0;", typ="mayaBinary", pr=True, es=True)
    print ("To Directory: " + ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb")
    mc.select(cl = True)



def ImportLatestShaders():
    SelectedShaderVer = mc.intField(ShaderVerInput, q = True, value = True)
    SceneGeometryList = mc.ls(selection = True)
    
    PreviouslyVisitedDirectories=[]
    
    #Checks if the user has selected any meshes
    #if nothing has been selected, select all geometry objects and apply shaders
    if(len(SceneGeometryList) == 0):
        print("No Meshes Selected - Importing All Shaders")
        AllSceneGeometryList = mc.ls(geometry=True)
        SceneGeometryList = AllSceneGeometryList
    else:
        print("Meshes Selected: " +str(SceneGeometryList)+ "Importing Shaders")

    for SceneGeometry in range(len(SceneGeometryList)):
        modelReferenceDir = mc.referenceQuery(SceneGeometryList[SceneGeometry], filename=True)
        ShaderPUB_Dir = modelReferenceDir.replace("model/source", "surfacing")
        ShaderPUB_DirArray=[]
        for DirSplitFwdSlsh in ShaderPUB_Dir.split('/'):
            ShaderPUB_DirArray.append(DirSplitFwdSlsh)
        FileNameArray=[]
        for DirSplitPeriod in ShaderPUB_DirArray[-1].split('.'):
            FileNameArray.append(DirSplitPeriod)
            
        BaseSurfacingName = FileNameArray[0] + ".v"
        BaseSurfacingName = BaseSurfacingName.replace("model", "surface")
        ShaderPUB_DirArray.remove(ShaderPUB_DirArray[-1])
        ShaderPUB_Dir = '/'.join(ShaderPUB_DirArray) + "/"
        
        
        fileIncrementer = 1
        while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
            fileIncrementer += 1
        ShaderVer = fileIncrementer - 1
        
        if(SelectedShaderVer > 0):
            ShaderVer = SelectedShaderVer
        
        
        
        LatestShaderMB_Dir = ShaderPUB_Dir + BaseSurfacingName + str(ShaderVer) +".mb"        #Shader Directory for most recent MayaBinary File
        LatestShaderJSON_Dir = ShaderPUB_Dir + BaseSurfacingName + str(ShaderVer) +".json"    #Shader Directory for most recent JSON File
        
        if(os.path.exists(LatestShaderMB_Dir) & os.path.exists(LatestShaderJSON_Dir)):
            if(LatestShaderMB_Dir not in PreviouslyVisitedDirectories):
                print("Latest version File Directory: " + LatestShaderMB_Dir)
                mc.file(LatestShaderMB_Dir, i=True, type="mayaBinary", ra=True, rdn=True, mnc=False, ns=FileNameArray[0], op="v=0", pr=True, an=True, itr="keep", mnr=True)
                
                PreviouslyVisitedDirectories.append(LatestShaderMB_Dir)
                
                with open(LatestShaderJSON_Dir, 'r') as infile:
                    data=infile.read()
                
                obj = json.loads(data)
                
                print(obj)
                for set in obj:
                    Obj_Material=[]
                    for i in set.split(':'):            
                        Obj_Material.append(i)
                    ObjTransformList = mc.ls("*:"+Obj_Material[0]+"*")
                    MaterialList = mc.ls("*"+Obj_Material[0]+":"+Obj_Material[1]+"*")
                    if(len(ObjTransformList) > 0 & len(MaterialList) > 0):
                        ObjTransform = ObjTransformList[0]
                        Material = MaterialList[0]
                        print("Mesh: " + ObjTransform + " | Material: " + Material + " | Shader Ver. Being Applied: " + str(ShaderVer))
                        
                        #selectedMesh = mc.listRelatives(ObjTransform, shapes=True)[0]
                        #print(selectedMesh)
                        #selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
                        #print(selectedMeshShading)
                        #selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
                        #print(selectedMat)
                        
                        mc.select(ObjTransform)
                        mc.hyperShade(assign=str(Material))
                        mc.select(cl=True)
                    else:
                        print("ERROR - Lighting Scene Model does not match published model, Expected: " + Obj_Material[0] + 
                              " | Recieved: " + SceneGeometryList[SceneGeometry] + " Please Update References")
                
                infile.close()
            
        else:
            print("ERROR - " + SceneGeometryList[SceneGeometry] + " Does Not Have Published Shader Version: " + str(ShaderVer))


def ApplyCustomShaders():
    
    selected=mc.select(mc.ls(geometry=True))
    
    
    if(selected):
        for i in selected:
            selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
            selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
            selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
            mc.connectAttr(f="lambert.outColour")
    
    mc.hyperShade(assign="lambert1")
    
    allmat=mc.ls(mat=True)
    basemat=mc.ls("*lambert1*","*standardSurface1*")
    
    allmat.remove(basemat[0])
    allmat.remove(basemat[1]) 
    allmat.remove("particleCloud1") 
    #for b in basemat:
    #    allmat.remove(b)
    for mat in allmat:
        mc.delete(mat)
    
    mc.select(cl=True)
    #ShaderVer = mc.intField(ShaderVerInput, q = True, value = True)
    #selected = mc.ls(selection = True)
    
    #if(len(selected) == 0):
    #    print("No Meshes Selected - Importing All Shaders")
    #    selected = mc.ls("*Geo")
    #    mc.select(selected)
    #    print(selected)
    #    for i in selected:
    #        children = mc.listRelatives(i, shapes=True, children=True, fullPath=True)
    #        print(children)
        
        #parents = mc.ls(selected, long=True)[0].split('|')[1:-1]
        #mc.select(parents)
        #print(parents)
        #parents.reverse()
        #parentGroup = parents[0]
        
        #print(parentGroup)
        
        #mc.select(parentGroup)
    
    #selected = mc.ls(selection = True)
    #mc.select(mc.ls(con=True))
    #parents = mc.ls(selected, long=True)[0].split('|')[1:-1]
    #parents.reverse()
    #parentGroup = parents[0]
    #print(parents[0])
    #print("ApplyLighting")
    
    

def ReloadLighting():
    #list of currently applied shaders
    #remove from list of all shaders
    #delete all shaders that are not currently applied
    
    #select every object and re-apply the most recent 
    
    AllShaders=[]
    AssignedShaders=[]
    UnassignedShaders=[]
    
    #¯\_(ツ)_/¯# Placeholder Function
    selected = mc.ls(mat=True)
    #mc.select(selected)
    for i in selected:
        AllShaders.append(i)
        AttachedObject = mc.hyperShade(o=str(i))
        print(AttachedObject)
        if(AttachedObject):
            AssignedShaders.append(i)
        print(i)
        mc.select(i)
        #mc.delete()
    print(AssignedShaders)
    print(AllShaders)




### Yucky Gui Stuff ###
if mc.window('Shader_Publishing', exists = True):
    mc.deleteUI('Shader_Publishing')
mc.window('Shader_Publishing', resizeToFitChildren = True)
mc.columnLayout(adjustableColumn = True, cal = "center", w=300)
mc.separator(h=10)
mc.text('SceneDirectory')
mc.separator(h=10)
mc.textField(tx = SceneDir)

mc.separator(h=10)
mc.text('Surfacing')
### Shader Exporting Functions ###
mc.separator(h=10)
mc.text('Select Objects to Publish')
mc.separator(h=10)
mc.button(label = 'Export Shaders to Publish', command = 'PublishShaders()', en = not isCurrentlyInLighting)


mc.separator(h=30)
mc.text('Lighting')
### Shader Importing Functions ###
mc.separator(h=10)
mc.text('Select Objects to Re-Apply Materials')
mc.separator(h=10)
mc.button(label = 'Apply Latest Shaders', command = 'ImportLatestShaders()', en = isCurrentlyInLighting)
mc.separator(h=10)


mc.gridLayout(ch=20,cw=150, nrc=[3,2], autoGrow= True)

mc.text('Enter Version Number:')
ShaderVerInput = mc.intField(width = 50, v=0, en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.button(label = '!!!Reset All Shaders!!!', command = 'ApplyCustomShaders()', en = isCurrentlyInLighting)
mc.button(label = 'Reload Shaders', command = 'ReloadLighting()', en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.showWindow('Shader_Publishing')