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


import daver
from easyhash import getSha1

APPNAME = 'distSolution'
VERSION = '1.1';
APPDISC = 'check files and archive them'

# global config
configs = {}


 




def checkShouldnotExistFile(dicregatedir, shouldnot):
    """ Return false if a file that should not be distributed exists. """
    for f in shouldnot:
        fullpath = dicregatedir + f
        if isfile(fullpath) or isdir(fullpath):
            myexit(fullpath + " exists.")
            return False
    
    return True
    
def checkShouldBeFiles(dicregatedir, shouldbe, shouldone):
    for f in shouldbe:
        fullpath = dicregatedir+f
        if( not (isfile(fullpath))):
            myexit(fullpath + " not exists.")
            return False
    
    if shouldone:
        oneofthem = False
        for f in shouldone:
            fullpath = dicregatedir+f
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
    
    checkShouldnotExistFile(outdir,configs["ShouldNotBeFiles"])
    checkShouldBeFiles(outdir, configs["ShouldBeFiles"], configs["ShouldBeOneOfThem"])

    if(configs['TotalFileCount'] != getFileCount(outdir)):
        myexit("{} != {}".format(configs['TotalFileCount'], getFileCount(outdir)))

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

    
def getMsBuildExe():
    pf = getenv("ProgramFiles");
    if pf:
        pf = os.path.join(pf, R"MSBuild\12.0\Bin\MSBuild.exe")
        if isfile(pf):
            return pf
        
    pf = getenv("ProgramFiles(x86)")
    if pf:
        pf = os.path.join(pf, R"MSBuild\12.0\Bin\MSBuild.exe")
        if isfile(pf):
            return pf
        
    return None

def build(solution,target):
    """build dicregate"""
    global configs
    
    msbuildexe = getMsBuildExe()
    if not msbuildexe:
        myexit("MSBuild.exe not found.")
     

    args = [
        msbuildexe,
        solution,
#         "/t:zzzDistResource",
#         "/p:Configuration=zzzDist",
        "/p:Platform={}".format(target["platform"])
    ]
    
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
    with open(sys.argv[1]) as data_file:
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
    archiveexe = os.path.join(configs["archivedir"], "{}-{}{}".format(configs["name"], verstring, ".exe"));
    if isfile(archiveexe):
        myexit('{} already exists, remove it first.'.format(archiveexe))
        
    print("==== creating arhive {} ====".format(archiveexe))
    
#    if(os.path.exists(archiveexe)):
#        print("{} already exists. Remove it first.".format(archiveexe))
#        myexit(1)
    
    args = [
        r"C:\LegacyPrograms\7-Zip\7z.exe",
        "a",
        "-sfx7z.sfx",
        archiveexe,
    ]
    
    for t in configs['targets']:
        args.append(t['outdir'])
        
    args.append("-mx9");
    
    print(args)
    subprocess.check_call(args)

    # upload
    print("Uploading to {}...".format(configs["remotedir"]))
    daver.dupload(configs["remotedir"], archiveexe)
    print("Uploaded to {}".format(configs["remotedir"]))
    
    
    print("Compute sha1 and compare...")
    localSha1 = getSha1(archiveexe)
    remoteSha1Url = configs["remotedir"] + "getSha1.php?file={}".format(archiveexe)
    remoteSha1 = urllib.request.urlopen(remoteSha1Url).read().decode("utf-8")
    
    if localSha1.lower() != remoteSha1.lower():
        myexit("sha1 not equal ({} != {}".format(localSha1, remoteSha1))
        
    print("sha1 check succeed ({})".format(localSha1))
    
def myexit(message, retval=1):
    print(message)
    # input('Press ENTER to exit')
    exit(retval)
    
def codetest():
    remoteSha1 = urllib.request.urlopen("http://ambiesoft.fam.cx/ffdav/uploads/dicregate/getSha1.php?file={}".format("Dicregate-3.1.1.11.exe")).read().decode("utf-8")
    print(remoteSha1)
    
if __name__ == "__main__":
    # codetest()
    
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    
    print("Disribution Succeeded ({} sec)".format(stop-start))
    # input('Press ENTER to exit')
    
