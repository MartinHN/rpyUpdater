import os
from os import walk
from shutil import copyfile
import platform
import subprocess
from Utils import is_connected,fillCfgAtPath,CustomErrRes
from time import sleep

isOSX = platform.system()=="Darwin"
simulateInTmp = isOSX

isConnectedToNet = False


defaultActionCfg  ={
  "timeout":120,
  "internetTimeout":0, #if specified
  "scriptGroup" : 0,
  
}

class Action(object):
  def __init__(self,name,path,exCMD = "sh"):
    self.name = name;
    self.path = path;
    self.exCMD = exCMD;
    self.etcDir = "/etc"
    self.cfg = defaultActionCfg.copy()
    self.parseErrors = fillCfgAtPath(path,self.cfg)
    if self.parseErrors:
      print("parsing error",self.parseErrors)
    if(simulateInTmp):
      self.etcDir = "/tmp/etc"


  def getFullExecutableCMD(self):
    return "%s %s"%(self.exCMD ,self.path)

  def doAction(self):
    if self.parseErrors:
      return CustomErrRes(self.parseErrors)

    cmd = self.getFullExecutableCMD()
    print(self.cfg,cmd)
    

    if(self.cfg["internetTimeout"]>0):
      remainingConnectionAttempts = self.cfg["internetTimeout"]
      connected = is_connected()
      while (not connected) and remainingConnectionAttempts:
        sleep(1)
        connected = is_connected()
        remainingConnectionAttempts-=1
      if(not connected):
        return CustomErrRes("not connected to internet")
    
    
    try:
      print (self.cfg["timeout"])
      return subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=self.cfg["timeout"])
    except:
      return CustomErrRes("hung")
      
    
    




class ChangeHostNameAction(Action):
  def __init__(self,path):
    super().__init__("changeHostName",path,"none")
    self.needRebootNow = True
    with  open(self.etcDir+'/hostname','r') as fp:
      self.currentHostName = fp.readline().strip()
    with  open(self.path,'r') as fp:
      self.newHostName = fp.readline().strip()
    self.cfg["scriptGroup"] = 0

  
  def getFullExecutableCMD(self):
    if(self.currentHostName==self.newHostName):
      return ""

    etcDirectory = "/etc"
    baseSED = "sed -i"
    if(isOSX):
      baseSED = "sed -i '' -e"
    sedCMD =baseSED+' "s/%s/%s/g" '%(self.currentHostName,self.newHostName)
    return sedCMD+self.etcDir+"/hosts && "+sedCMD+self.etcDir+"/hostname;"


class UpdateMe(Action):
  def __init__(self,path):
    super().__init__("updateMe",path,"none")
    self.cfg["internetTimeout"] = 60
    self.gitDirectory = os.path.dirname(os.path.realpath(__file__))
    self.cfg["scriptGroup"] = -1

  def getFullExecutableCMD(self):
    return "cd %s && git pull"%self.gitDirectory
  



def buildActionFromFile(f):
  fileName = os.path.basename(f)
  if(fileName.lower()=="hostname"):
    return ChangeHostNameAction(f)
  elif(fileName.lower()=="updateme"):
    return UpdateMe(f)
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
  res.sort(key=lambda r:r.cfg["scriptGroup"])
  return res


def createBaseStructure(folderToWatch):
  directories = { x:os.path.join(folderToWatch,x) for x in ['logs','quarantine','done']}
  for directory in directories.values():
    if not os.path.exists(directory):
      os.makedirs(directory)
  return directories

def parseNRun(folderToWatch,isOnce): # return true if at least on action succeed
  actions = []
  if os.path.exists(folderToWatch):
    specialDirs = createBaseStructure(folderToWatch)
    actions = buildActionList(os.path.join(folderToWatch))

  numActionsSuccess =0

  if len(actions):
    lastscriptGroup = actions[0].cfg["scriptGroup"]
    for a in actions:
      if(lastscriptGroup!=a.cfg["scriptGroup"]):
        break
      lastscriptGroup = a.cfg["scriptGroup"]
      if(processActionResult(a.doAction(),a,specialDirs,isOnce)):
        numActionsSuccess +=1
  else:
    print("nothing to do at ",folderToWatch)
  return (len(actions)>0) and numActionsSuccess>0


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
    if (not a.cfg["internetTimeout"]>0) or is_connected(): # keep if internet connection not active
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
  return res.returncode==0




if __name__=="__main__":
  folderToWatch = "/boot/customConfig"
  if(isOSX):
    folderToWatch = "/tmp/customConfig"
  if(parseNRun(folderToWatch+"/once",True)):
    rebootCmd = "sudo reboot"
    if  not isOSX:
      subprocess.run(rebootCmd,shell=True)
    else:
      print (rebootCmd)

  parseNRun(folderToWatch+"/each",False)
  exit(0)



