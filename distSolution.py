import sys
import os
from os.path import isfile, isdir
import subprocess
import re
from os import getenv
import timeit
import glob
import json
import urllib.request
import time

import daver
from easyhash import getSha1

APPNAME = 'distSolution'
VERSION = '1.1';
APPDISC = 'check files and archive them'

# global config
configs = {}


 




def checkShouldnotExistFile(distDir, shouldnot):
    """ Return false if a file that should not be distributed exists. """
    for f in shouldnot:
        fullpath = os.path.join(distDir, f)
        if isfile(fullpath) or isdir(fullpath):
            myexit(fullpath + " exists.")
            return False
    
    return True
    
def checkShouldBeFiles(distDir, shouldbe):
    for f in shouldbe:
        fullpath = os.path.join(distDir,f)
        if( not (isfile(fullpath))):
            myexit(fullpath + " not exists.")
            return False
    
    
    return True

def checkShouldOneOfFiles(distDir, shouldone):
    
    if shouldone:
        oneofthem = False
        for f in shouldone:
            fullpath = distDir+f
            if(isfile(fullpath)):
                if(oneofthem):
                    myexit(fullpath + " One of them files duplicating.")
                    return False
                oneofthem = True
                
        if(not oneofthem):
            myexit("None of oneofthem files exists.")
            return False
    
    return True
            
def getFileCount(d):
    total = 0
    for _, _, files in os.walk(d):
        total += len(files)
    return total


def checkTarget(target):
    global configs
    
    outdir = target['outdir'];
    print("=== Start Testing {} ===".format(outdir))
    
    if "ShouldNotBeFiles" in configs:
        checkShouldnotExistFile(outdir,configs["ShouldNotBeFiles"])
    
    if "ShouldBeFiles" in configs:
        checkShouldBeFiles(outdir, configs["ShouldBeFiles"])
        
    if "ShouldBeOneOfThem" in configs:
        checkShouldOneOfFiles(outdir, configs["ShouldBeOneOfThem"])

    if(configs['TotalFileCount'] != getFileCount(outdir)):
        myexit("TotalFileCount different. ({} != {})".format(configs['TotalFileCount'], getFileCount(outdir)))

    print ("Total file count = {}".format(getFileCount(outdir)))    

def getVersionString(target):
    """get version string from history.txt"""
    global configs
    
    outdir = target['outdir'];
    
    fileName = os.path.join(outdir, configs["obtainverfrom"])
    with open(fileName, "r", encoding="utf-8") as f:
        lines = f.readlines()
        line=lines[0]
        regstr = configs["obtainverregex"]
        m = re.search(regstr, line)
        return m.group(0)
    
    myexit("Version not found.")

def getMsBuildExe2(pf, vsvar):
    if pf:
        if vsvar==12:
            pf = os.path.join(pf, R"MSBuild\12.0\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
        elif vsvar==15:
            pf = os.path.join(pf, R"Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
    return None
 
def getMsBuildExe(solution):
    vsvar = 0
    # Get VS version from solution file
    with open(solution, "r", encoding="utf-8") as f:
        lines=f.readlines()
        for line in lines:
            vsvermatch = re.search('VisualStudioVersion\\s=\\s(?P<topver>\\d+)',line)
            if not vsvermatch:
                continue
            topver = int(vsvermatch.group('topver'))
            if topver==12:
                print ("solution is for Visual Studio 12")
                vsvar=12
                break
            elif topver==15:
                print ("solution is for Visual Studio 15")
                vsvar=15
                break
                
    if not vsvar:
        myexit('Could not find VS version from solution')

    pf = getMsBuildExe2(getenv("ProgramFiles"),vsvar)
    if pf and isfile(pf):
        return pf
    
    pf = getMsBuildExe2(getenv("ProgramFiles(x86)"),vsvar)      
    if pf and isfile(pf):
        return pf

    return None

def build(solution,target):
    """build target of solution"""
    global configs
    
    msbuildexe = getMsBuildExe(solution)
    if not msbuildexe:
        myexit("MSBuild.exe not found.")
     

    args = [
        msbuildexe,
        solution,
#        "/t:zzzDistResource",
#        "/p:Configuration=zzzDist",
#        "/p:Platform={}".format(target["platform"])
    ]
    
    if "platform" in target:
        args.append("/p:platform={}".format(target["platform"]))
 
    if "setoutdirforbuild" in target and target["setoutdirforbuild"]:
        outDirBuild = target["outdir"]
        outDirBuild = os.path.join(outDirBuild, '')  # will add the trailing slash if it's not already there.
        args.append('/p:outdir={}'.format(outDirBuild))
               
    if "targetproject" in configs:
        args.append("/t:{}".format(configs["targetproject"]))

    if "configuration" in configs:
        args.append("/p:Configuration={}".format(configs["configuration"]))
        
    print(args)
    subprocess.check_call(args)

# def getSolutionFile(solutionDir):
#     '''get *.sln from dir'''
#     fs = glob.glob(os.path.join(solutionDir,"*.sln"))
#     
#     if len(fs) != 1:
#         myexit('not 1 solution file found ({}).'.format(fs))
        
HELPSTRING="""
distSolution distConfig
distConfig is json file, see the following expamle

{
    'solutoion': 'aaa.sln'
    [
            { 
                "outdir" : "C:/Linkout/Dicregate/",
                "platform":"Win32"
            },

              
            {
                "outdir" : "C:/Linkout/Dicregate64/",
                "platform":"x64"
            }
    ]
}
"""
   
def main():
    if sys.version_info[0] < 3:
        myexit("Please use python3" + sys.version)
        
    print('{} {} ({})'.format(APPNAME,VERSION,APPDISC))
    
    if len(sys.argv) < 1:
        myexit("No input file." + HELPSTRING)
    
    global configs    
    print("Opening input {}".format(sys.argv[1]))
    with open(sys.argv[1],encoding="utf-8") as data_file:
        configs = json.load(data_file)
          

    solutionFile = os.path.join(os.path.dirname(sys.argv[1]), configs["solution"])
    
#     targets = (
#             { 
#                 "solutionfile":solutionFile,
#                 "outdir" : R"C:/Linkout/Dicregate/",
#                 "platform":"Win32"
#             },
# 
#               
#             {
#                 "solutionfile":solutionFile,
#                 "outdir" : R"C:/Linkout/Dicregate64/",
#                 "platform":"x64"
#             }
#     )
    verstring="";
    
    # build first
    for target in configs['targets']:
        build(solutionFile, target)

    # check        
    for target in configs['targets']:
        checkTarget(target)
        vstT = getVersionString(target)
        if(verstring and verstring != vstT):
            myexit("different is verstion in 32 and 64.")

        verstring = vstT
        

#     target = targets[0];
#     outdir=target['outdir']
#     parentDir = os.path.abspath(os.path.join(outdir, os.pardir))
#     dirName = os.path.basename(os.path.dirname(outdir))

    #archive it

    archiveexe = "{}-{}{}".format(configs["name"], verstring, ".exe")
    archiveexefull = os.path.join(configs["archivedir"], archiveexe)
    if isfile(archiveexefull):
        myexit('{} already exists, remove it first.'.format(archiveexefull))
        
    print("==== creating arhive {} ====".format(archiveexefull))
    
#    if(os.path.exists(archiveexefull)):
#        print("{} already exists. Remove it first.".format(archiveexefull))
#        myexit(1)
    
    args = [
        r"C:\LegacyPrograms\7-Zip\7z.exe",
        "a",
        "-sfx7z.sfx",
        archiveexefull,
    ]
    
    
    # no duplicate in args
    addedtarget=[]
    for t in configs['targets']:
        outdir = t['outdir']
        if outdir not in addedtarget:
            outdirfull = os.path.abspath(outdir)
            args.append(outdirfull)
        addedtarget.append(outdir)
        
    args.append("-mx9");
    
    print(args)
    subprocess.check_call(args)

    # upload
    print("==== Uploading to {}... ====".format(configs["remotedir"]))
    daver.dupload(configs["remotedir"], archiveexefull)
    print("Uploaded to {}".format(configs["remotedir"]))
    
    
    print("==== Compute sha1 and compare... ====")
    localSha1 = getSha1(archiveexefull)
    remoteSha1Url = configs["remotesha1"].format(archiveexe)

    for loop in range(100):
        try:
            remoteSha1 = urllib.request.urlopen(remoteSha1Url).read().decode("utf-8")
            break
        except:
            print("failed {} times to check remote Sha1. Will try again after waiting 5 seconds.".format(loop+1))
            time.sleep(5) # wait 5 seconds
    
    if localSha1.lower() != remoteSha1.lower():
        myexit("sha1 not equal ({} != {}".format(localSha1, remoteSha1))
        
    print("sha1 check succeed ({})".format(localSha1))
    
def myexit(message, retval=1):
    
    print('DistError: ' + message)
    # input('Press ENTER to exit')
    exit(retval)
    
def codetest():
    remoteSha1 = urllib.request.urlopen("http://ambiesoft.fam.cx/ffdav/uploads/getSha1.php?file={}".format("/test/test.txt")).read().decode("utf-8")
    print(remoteSha1)
    
if __name__ == "__main__":
    # codetest()
    
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    
    m, s = divmod(stop - start, 60)
    h, m = divmod(m, 60)
    elapsed = "%d:%02d:%02d" % (h, m, s)
    
    print()
    print("==== Disribution Succeeded (elapsed: {}) ====".format(elapsed))
    
    

    # input('Press ENTER to exit')
    
