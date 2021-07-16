import preinstall
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
from argparse import ArgumentParser
import daver
from easyhash import getSha1
from updateBBS import updateBBS
from funcs import getAsFullpath,getPathDiffs,getFileListAsFullPath,myexit,showDiffAndExit,IsRemoteArchiveExists,getChangeLog,getFileCount
from collections import Counter

APPNAME = 'distSolution'
VERSION = '1.2.4'
APPDISC = 'build, check files, archive them and distribute solution'

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

    shouldBeFull = getAsFullpath(configs["ShouldBeFiles"], outdir)
    
    if(('TotalFileCount' not in configs) or configs['TotalFileCount']== "exact"):
        showDiffAndExit(outdir,shouldBeFull,configs['TotalFileCount'],True)
    elif(isinstance( configs['TotalFileCount'], int)):
        if(configs['TotalFileCount'] != getFileCount(outdir)):
            showDiffAndExit(outdir,shouldBeFull,configs['TotalFileCount'],False)
    else:
        myexit("[TotalFileCount] must be int or 'exact'")
      
    print ("Total file count = {}".format(getFileCount(outdir)))    

def getVersionString(target):
    """get version string from history.txt"""
    global configs
    
    outdir = target['outdir'];
    
    fileName = os.path.join(outdir, configs["obtainverfrom"])
    with open(fileName, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines:
          regstr = configs["obtainverregex"]
          m = re.search(regstr, line)
          if(m):
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
        elif vsvar==16:
            pf = os.path.join(pf, R"Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
    return None
 
def getDevenvExeOrCom2(pf, vsvar, ext):
    if pf:
        if vsvar==12:
            pf = os.path.join(pf, R"Microsoft Visual Studio 12.0\Common7\IDE\devenv" + ext)
            if isfile(pf):
                return pf
        # elif vsvar==15:
        #     pf = os.path.join(pf, R"Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe")
        #     if isfile(pf):
        #         return pf
        elif vsvar==16:
            pf = os.path.join(pf, R"Microsoft Visual Studio\2019\Community\Common7\IDE\devenv" + ext)
            if isfile(pf):
                return pf
    return None
 
def getVsVerFromSln(sln):
    vsvar = 0
    # Get VS version from solution file
    with open(sln, "r", encoding="utf-8") as f:
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
            elif topver==16:
                print ("solution is for Visual Studio 2019")
                vsvar=16
                break
    return vsvar

def getMsBuildExe(solution):
    vsvar = getVsVerFromSln(solution)

    if not vsvar:
        myexit('Could not find VS version from solution')

    pf = getMsBuildExe2(getenv("ProgramFiles"),vsvar)
    if pf and isfile(pf):
        return pf
    
    pf = getMsBuildExe2(getenv("ProgramFiles(x86)"),vsvar)      
    if pf and isfile(pf):
        return pf

    return None

def getDevenvExeOrCom(solution, ext='.com'):
    vsvar = getVsVerFromSln(solution)

    if not vsvar:
        myexit('Could not find VS version from solution')

    pf = getDevenvExeOrCom2(getenv("ProgramFiles"),vsvar,ext)
    if pf and isfile(pf):
        return pf
    
    pf = getDevenvExeOrCom2(getenv("ProgramFiles(x86)"),vsvar,ext)      
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
        outDirBuild = os.path.abspath(target["outdir"])
        outDirBuild = os.path.join(outDirBuild, '')  # will add the trailing slash if it's not already there.
        args.append('/p:outdir={}'.format(outDirBuild))
               
    if "targetproject" in configs:
        args.append("/t:{}".format(configs["targetproject"]))

    if "configuration" in configs:
        args.append("/p:Configuration={}".format(configs["configuration"]))
        
    print(args)
    subprocess.check_call(args)

def checkArchivingDir(archivingfull, outdirsfull):
    ''' archivingfull must constans dirs only '''
    # traverse root directory, and list directories as dirs and files as files
    dirs = os.listdir(archivingfull)
    dirsfull = [os.path.join(archivingfull,dir) for dir in dirs]
    # compare efficiently
    if Counter(dirsfull) != Counter(outdirsfull):
        myexit('archivingdir is not equal to outdirs')

        
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
   
def getGitHash(gitdir, git):
    ''' get hash from dir'''

    args = [git, '-C', gitdir, 'rev-parse', 'HEAD']
    print(args)
    hash = subprocess.check_output(args).decode('utf-8').strip()
    if len(hash) != 40:
        exit('hex digits of hash is not 40')
    return hash

CPPCODEHEAD='''// DO NOT EDIT
// This file was created and will be overwritten by distSolution.py
// DO NOT EDIT
'''

CPPCODEPREV='''
#ifndef GITREV_INCLUDED_
#define GITREV_INCLUDED_

#include <string>
#include <sstream>
namespace GITREV {
    static constexpr %(cppchar)s *hashes[][2] =  {

'''

CPPCODEPOST='''
    };
    inline %(cppstring)s GetHashMessage() {
        %(cppstringstream)s message;
        for (auto&& s : hashes)
            message << s[0] << %(literalL)s"=" << s[1] << std::endl;
        return message.str();
    }
}  // namespace GITREV
#endif  // GITREV_INCLUDED_
'''

def createGitRev(gitrev, ShowDummy=False, DummyType='cpp', Char='char'):
    ''' create or change gitrev.h from git hash '''
    if not ShowDummy:
        if not gitrev:
            return
        if not gitrev['gitdirs']:
            exit('"gitdirs" must be specified in "gitrev"')
        if not gitrev['outheader'] and not gitrev['outtxt']:
            exit('"outheader" or "outtxt" must be specified in "gitrev"')
    
        # find git executable
        for g in gitrev['gits'] if gitrev['gits'] else ['git']:
            if not os.path.isfile(g):
                continue
            git = g
            break
        if not git:
            git = 'git'

    # get hashes from git
    namehash = []
    if ShowDummy:
        namehash.append(['dummy', '0'*40])
    else:
        for gitdir in gitrev['gitdirs']:
            dir = os.path.basename(os.path.abspath(gitdir)).replace('.','').replace('/','').replace('\\','')
            if not dir:
                exit('dir is empty')
            hash = getGitHash(gitdir, git)
            namehash.append([dir,hash])

    # decide char or wchar
    if not ShowDummy and gitrev['char']:
        Char = gitrev['char']
    if Char == 'char':
        cppchar = 'char'
        cppstring = 'std::string'
        cppstringstream = 'std::stringstream'
        literalL = ''
    elif Char == 'wchar':
        cppchar = 'wchar_t'
        cppstring = 'std::wstring'
        cppstringstream = 'std::wstringstream'
        literalL = 'L'
    else:
        exit('Char must be char or wchar')

    if (gitrev and 'outheader' in gitrev) or (ShowDummy and DummyType=='cpp'):
        if ShowDummy:
            gitrevheader = sys.stdout;
            if not gitrevheader:
                exit('Failed to open stdout')    
        else:
            gitrevheader = open(gitrev['outheader'], 'w')
            if not gitrevheader:
                exit('Failed to open', gitrev['outheader'])
        
        gitrevheader.write(CPPCODEHEAD)

        insidemap = ''
        for nh in namehash:
            insidemap += '{' + literalL + '"' + nh[0] +  '",' + literalL + '"' + nh[1] + '"},\n'

        code = (CPPCODEPREV + insidemap + CPPCODEPOST) % {
            'cppchar': cppchar,
            'cppstring': cppstring,
            'cppstringstream': cppstringstream,
            'literalL': literalL,
        }

        gitrevheader.write(code)
        if gitrevheader != sys.stdout:
            gitrevheader.close()

    if (gitrev and 'outtxt' in gitrev) or (ShowDummy and DummyType=='txt'):
        if ShowDummy:
            gitrevtext = sys.stdout;
            if not gitrevtext:
                exit('Failed to open stdout')    
        else:
            gitrevtext = open(gitrev['outtxt'], 'w')
            if not gitrevtext:
                exit('Failed to open', gitrev['outtxt'])        
        
        revtext = ''
        for nh in namehash:
            revtext += '%s=%s\n' % (nh[0],nh[1])

        gitrevtext.write(revtext)
        if gitrevtext != sys.stdout:
            gitrevtext.close()

def getExtension(file, IncludeDot=True):
    ret = os.path.splitext(file)[1]
    if not IncludeDot:
        ret = ret.lstrip('.')
    return ret

def getInputfileType(inputfile):
    ''' determin inputfile is json or yaml '''
    ext = getExtension(inputfile, IncludeDot=False)
    if ext.lower()=='yaml':
        return 'yaml'
    return 'json'

def main():
    if sys.version_info[0] < 3:
        exit("Please use python3" + sys.version)
        
    # print('{} {} ({})'.format(APPNAME,VERSION,APPDISC))
    
    parser = ArgumentParser(
        prog="distSolution",
        description="Build VS Project")
        
    parser.add_argument(
        "-C",
        nargs='?',
        action="store",
        help="Set current directory.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="skip build process"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="skip check process"
    )
    parser.add_argument(
        "--skip-archive",
        action="store_true",
        help="skip archive process"
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="skip upload process"
    )
    parser.add_argument(
        "--skip-hashcheck",
        action="store_true",
        help="skip hashcheck process"
    )
    parser.add_argument(
        "--skip-bbs",
        action="store_true",
        help="skip bbs process"
    )
    parser.add_argument(
        "--show-dummygitrev",
        action="store_true",
        help="show c++ gitrev code in char. This can be use for the first code."
    )
    parser.add_argument(
        "--show-dummygitrev-wchar",
        action="store_true",
        help="show c++ gitrev code in wchar_t. This can be use for the first code."
    )
    parser.add_argument(
        "--show-dummygitrev-txt",
        action="store_true",
        help="show gitrev text. This can be use for the first dummy output."
    )
    parser.add_argument('inputfile',
        nargs='?')

    commandargs = parser.parse_args()

    if commandargs.C:
        os.chdir(commandargs.C)

    if commandargs.show_dummygitrev_wchar:
        createGitRev(None, ShowDummy=True, Char='wchar')
        exit(0)
    if commandargs.show_dummygitrev:
        createGitRev(None, ShowDummy=True)
        exit(0)
    if commandargs.show_dummygitrev_txt:
        createGitRev(None, ShowDummy=True, DummyType='txt')
        exit(0)

    global configs    
    
    if sys.stdin.isatty():
        if not commandargs.inputfile:
            exit('No input input file')
        distFile = commandargs.inputfile
        filetype = getInputfileType(distFile)
        print("Opening input {} as {}".format(distFile, filetype))
        with open(distFile,encoding="utf-8") as data_file:
            if filetype=='yaml':
                import yaml
                configs = yaml.safe_load(data_file)
            else:
                configs = json.load(data_file)
    else:
        # read from pipe
        configs = json.load(sys.stdin)

    # create gitrev.h if specified          
    if 'gitrev' in configs:
        createGitRev(configs['gitrev'])

    if not 'solution' in configs:
        exit('"solution" is not specifed')

    solutionFile = os.path.join(os.path.dirname(distFile), configs["solution"])
    verstring="";
    
    # build first
    if not commandargs.skip_build:
        for target in configs['targets']:
            build(solutionFile, target)

    # check      
    for target in configs['targets']:
        if not commandargs.skip_check: 
            checkTarget(target)
        vstT = getVersionString(target)
        if(verstring and verstring != vstT):
            myexit("different is verstion between targets.")
        verstring = vstT
        

    #archive it
    archiveexe = "{}-{}{}".format(configs["name"], verstring, ".exe")
    archiveexefull = os.path.join(configs["archivedir"], archiveexe)
    if not commandargs.skip_archive:
        if isfile(archiveexefull):
            myexit('{} already exists, remove it first.'.format(archiveexefull))
     
    urlfull = configs['remotedir'] + archiveexe
    if not commandargs.skip_upload:
        if IsRemoteArchiveExists(urlfull):
            myexit('{} already exists'.format(urlfull))
    
               
    if not commandargs.skip_archive:
        print("==== creating arhive {} ====".format(archiveexefull))
        args7z = [
            r"C:/LegacyPrograms/7-Zip/7z.exe",
            "a",
            "-sfx7z.sfx",
            archiveexefull,
        ]
        
        if 'archivingdir' in configs:
            # check the archivingdir only contains outdirs
            archivingfull = os.path.abspath(configs['archivingdir'])
            outdirsfull = []
            for target in configs['targets']:
                outdirsfull.append(os.path.abspath(target['outdir']))
            checkArchivingDir(archivingfull, outdirsfull)

            args7z.append(archivingfull)
        else:
            # no duplicate in args7z
            addedtarget=[]
            for t in configs['targets']:
                outdir = t['outdir']
                if outdir not in addedtarget:
                    outdirfull = os.path.abspath(outdir)
                    args7z.append(outdirfull)
                addedtarget.append(outdir)
            
        args7z.append("-mx9");
        
        print(args7z)
        subprocess.check_call(args7z)



    # upload
    if not commandargs.skip_upload:
        print("==== Uploading to {}... ====".format(configs["remotedir"]))
        daver.dupload(configs["remotedir"], archiveexefull)
        print("Uploaded to {}".format(configs["remotedir"]))
    
    
    if not commandargs.skip_hashcheck:
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
    

    ## update BBS
    if not commandargs.skip_bbs:
        print("==== Updating BBS... ====")
        historyFull = os.path.join(configs['targets'][0]['outdir'],
                                configs['obtainverfrom'])
        versionReg = configs['obtainverregex']
        print(updateBBS( configs['name'], 
                        verstring, 
                        configs["remotedir"] + archiveexe,
                        getChangeLog(historyFull, versionReg)
                        ))
    

    ######################
    ######################

    
def codetest():
    print(updateBBS("testproject", "1.0", "file.zip"))
    
    remoteSha1 = urllib.request.urlopen("http://ambiesoft.mooo.com/ffdav/uploads/getSha1.php?file={}".format("/test/test.txt")).read().decode("utf-8")
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
    
