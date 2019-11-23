import os


#####################
## Internet

import socket
def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False


#####################@@
###  CFG




def isComment(l):
  return l.startswith("#")

def parseCfgCMD(l,cfg):
  spl = l.split("rpy.")
  errs = []
  if len (spl)>1:
    cmd = spl[1].split(":")
    if len(cmd)>1:
      k = cmd[0].strip()
      v = int(cmd[1].strip())
      if not k in cfg.keys():
        errs+= ["wrong config Arg : %s"%(k)]
      else:
        print("custom cfg %s : %i"%(k,v))
        cfg[k] = v
    else:
      errs+= ["wrong config formating in %l, no : found"]
      
  return errs

def parsCfgHeader(filePath,cfg):
  errs = []
  if(os.path.exists(filePath)):
    with open(filePath,'r') as fd:
      l = fd.readline().strip()
      if l.strip().startswith("#!"):
        l = fd.readline().strip()
      while isComment(l)  or l=="":
        errs+=parseCfgCMD(l,cfg)
        l=fd.readline().strip()
  return errs


def fillCfgAtPath(scriptPath,cfg):
  return parsCfgHeader(scriptPath,cfg)

###############################
## subprocess

class CustomErrRes(object):
  def __init__(self,err):
    self.returncode=-1
    self.stderr = str(err)
    self.stdout=""

