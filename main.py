import os
from os import walk
from shutil import copyfile
import platform
import subprocess
isOSX = platform.system()=="Darwin"
simulateInTmp = isOSX

class Action(object):
  def __init__(self,name,path,exCMD = "sh"):
    self.name = name;
    self.path = path;
    self.exCMD = exCMD;
    self.etcDir = "/etc"
    if(simulateInTmp):
      self.etcDir = "/tmp/etc"


  def getFullExecutableCMD(self):
    return "%s %s"%(self.exCMD ,self.path)

  def doAction(self):
    cmd = self.getFullExecutableCMD()
    print(cmd)
    return subprocess.run(cmd,shell=True,capture_output=True,text=True)
    

class ChangeHostNameAction(Action):
  def __init__(self,path):
    super().__init__("changeHostName",path,"none")
    with  open(self.etcDir+'/hostname','r') as fp:
      self.currentHostName = fp.readline().strip()
    with  open(self.path,'r') as fp:
      self.newHostName = fp.readline().strip()

  def getFullExecutableCMD(self):
    if(self.currentHostName==self.newHostName):
      return ""

    etcDirectory = "/etc"
    baseSED = "sed -i"
    if(isOSX):
      baseSED = "sed -i '' -e"
    sedCMD =baseSED+' "s/%s/%s/g" '%(self.currentHostName,self.newHostName)
    return sedCMD+self.etcDir+"/hosts && "+sedCMD+self.etcDir+"/hostname;"


def buildActionFromFile(f):
  fileName = os.path.basename(f)
  if(os.path.basename(f).lower()=="hostname"):
    return ChangeHostNameAction(f)
  elif f.endswith(".py"):
    return Action(fileName,f,"python3")
  elif f.endswith(".sh"):
    return Action(fileName,f,"sh")


def buildActionList(folder):
  res = []
  if os.path.exists(folderToWatch):
    for (dirpath, dirnames, filenames) in walk(folder):
      if(dirpath==folder):
        for f in filenames:
          a = buildActionFromFile(os.path.join(dirpath,f))
          if a:
            res+=[a]
  return res


def createBaseStructure(folderToWatch):
  directories = { x:os.path.join(folderToWatch,x) for x in ['logs','quarantine','done']}
  for directory in directories.values():
    if not os.path.exists(directory):
      os.makedirs(directory)
  return directories

def parseNRun(folderToWatch,isOnce):
  actions = []
  if os.path.exists(folderToWatch):
    specialDirs = createBaseStructure(folderToWatch)
    actions = buildActionList(os.path.join(folderToWatch))

  if len(actions):
    for a in actions:
      processActionResult(a.doAction(),a,specialDirs,isOnce)
  else:
    print("nothing to do at ",folderToWatch)
    
def writeOrRemove(filePath,data):
  if(data):
    with open(filePath,'w') as fp:
      fp.write(data)
  elif os.path.exists(filePath):
    os.remove(filePath)

def processActionResult(res,a,specialDirs,isOnce):
  srcFile = a.path
  dstDir = os.path.dirname(srcFile)
  logFile = os.path.join(specialDirs["logs"],os.path.basename(srcFile));
  if(res.returncode!=0):
    targetFile = os.path.join(specialDirs["quarantine"],os.path.basename(srcFile))
    os.rename(srcFile,targetFile)
  else:
    targetFile = os.path.join(specialDirs["done"],os.path.basename(srcFile))
    if(srcFile!=targetFile):
      copyfile(srcFile,targetFile)
    if isOnce:
      os.remove(srcFile)

  writeOrRemove(logFile+".err",res.stderr)
  writeOrRemove(logFile+".log",res.stdout)




if __name__=="__main__":
  folderToWatch = "/boot/customConfig"
  folderToWatch = "/tmp/customConfig"
  parseNRun(folderToWatch+"/once",True)
  parseNRun(folderToWatch+"/each",False)




