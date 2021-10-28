import json
import os
import re
import sys
import subprocess
import daver
from easyhash import getSha1
import urllib.request
import time
from funcs import myexit,showDiffAndExit,getAsFullpath,IsRemoteArchiveExists,getChangeLog
import certifi
from lsPy import lspy

def getFileCount(d):
    total = 0
    for _, _, files in os.walk(d):
        total += len(files)
    return total


            
class DistConfig:
    __version = ''
    
    def __init__(self, path):
            with open(path,encoding="utf-8") as data_file:
                self.configs = json.load(data_file)
                

    def getProjectName(self):
        return self.configs['name']

    def getRemoteDir(self):
        return self.configs["remotedir"]                        
    
    def checkGitrev(self):
        if 'gitrev' in self.configs:
            createGitRev(self.configs['gitrev'])

    def checkShouldnotExistFile(self, distDir, shouldnot):
        """ Return false if a file that should not be distributed exists. """
        for f in shouldnot:
            fullpath = os.path.join(distDir, f)
            if os.path.isfile(fullpath) or os.path.isdir(fullpath):
                myexit(fullpath + " exists.")
                return False
    
        return True
                    
                    
    def checkShouldBeFiles(self, distDir, shouldbe):
        for f in shouldbe:
            fullpath = os.path.join(distDir,f)
            if( not (os.path.isfile(fullpath))):
                myexit(fullpath + " not exists.")
                return False
        
        return True
                    
                    
    def checkShouldOneOfFiles(self, distDir, shouldone):
        if shouldone:
            oneofthem = False
            for f in shouldone:
                fullpath = distDir+f
                if(os.path.isfile(fullpath)):
                    if(oneofthem):
                        myexit(fullpath + " One of them files duplicating.")
                        return False
                    oneofthem = True
                    
            if(not oneofthem):
                myexit("None of oneofthem files exists.")
                return False
        
        return True
                    
                    
    def getVersionString(self, outdir):
        """get version string from history.txt"""
        if self.__version:
            return self.__version
        configs = self.configs
        
        fileName = os.path.join(outdir, configs["obtainverfrom"])
        with open(fileName, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line=lines[0]
            regstr = configs["obtainverregex"]
            m = re.search(regstr, line)
            
            self.__version = m.group(0)
            return self.__version
        
        myexit("Version not found.")

    def getChangeLong(self,outdir):
        configs = self.configs
        fileName = os.path.join(outdir, configs["obtainverfrom"])
        regstr = configs["obtainverregex"]
        
        return getChangeLog(fileName, regstr)
     
                                    
    def checkTarget(self, outdir):
        configs = self.configs
        
        print("=== Start Testing {} ===".format(outdir))
        
        if "ShouldNotBeFiles" in configs:
            self.checkShouldnotExistFile(outdir,configs["ShouldNotBeFiles"])
        
        if "ShouldBeFiles" in configs:
            self.checkShouldBeFiles(outdir, configs["ShouldBeFiles"])
            
        if "ShouldBeOneOfThem" in configs:
            self.checkShouldOneOfFiles(outdir, configs["ShouldBeOneOfThem"])
    
        shouldBeFull = getAsFullpath(configs["ShouldBeFiles"], outdir)
        
        if(('TotalFileCount' not in configs) or configs['TotalFileCount']== "exact"):
            showDiffAndExit(outdir,shouldBeFull,configs['TotalFileCount'],True)
        elif(isinstance( configs['TotalFileCount'], int)):
            if(configs['TotalFileCount'] != getFileCount(outdir)):
                showDiffAndExit(outdir,shouldBeFull,configs['TotalFileCount'],False)
        else:
            myexit("[TotalFileCount] must be int or 'exact'")
          
        print ("Total file count = {}".format(getFileCount(outdir))) 

   
        
        
    def getArchiveName(self,verstring):
        configs = self.configs
        return "{}-{}{}".format(configs["name"], verstring, ".exe")
        
    def getArchiveFull(self,verstring):
        configs = self.configs
        self.archiveexe = "{}-{}{}".format(configs["name"], verstring, ".exe")
        self.archiveFull = os.path.join(configs["archivedir"], self.archiveexe)
        return self.archiveFull

    def createArchive(self, path7z, targetdir, verstring):
        # configs = self.configs
        
        archiveexefull = self.getArchiveFull(verstring)
        if os.path.isfile(archiveexefull):
            myexit('{} already exists, remove it first.'.format(archiveexefull))

        args = [
            path7z,
            "a",
            "-sfx7z.sfx",
            archiveexefull,
            targetdir,
        ]
        
        args.append("-mx9")
        
        print(args)
        subprocess.check_call(args)
        
    def checkAlreadyUploaded(self, verstring):
        """ check remote archive exist and quit if true. """
        configs = self.configs
        
        url = configs['remotedir'] + self.getArchiveName(verstring)
        
        print("checking {} ...".format(url))
        if IsRemoteArchiveExists(url):
            myexit("Archive already exists in remote site {0}. quitting.".format(url))
            

        
        
    def upload(self):
        configs = self.configs
        
        archiveexefull = self.archiveFull
        
        print("==== Uploading to {}... ====".format(configs["remotedir"]))
        daver.dupload(configs["remotedir"], archiveexefull)
        print("Uploaded to {}".format(configs["remotedir"]))
        
        
        print("==== Compute sha1 and compare... ====")
        localSha1 = getSha1(archiveexefull)
        remoteSha1Url = configs["remotesha1"].format(self.archiveexe)
    
        for loop in range(100):
            try:
                remoteSha1 = urllib.request.urlopen(remoteSha1Url, cafile=certifi.where() ).read().decode("utf-8")
                break
            except:
                print("failed {} times to check remote Sha1. Will try again after waiting 5 seconds.".format(loop+1))
                time.sleep(5) # wait 5 seconds
        
        if localSha1.lower() != remoteSha1.lower():
            myexit("sha1 not equal ({} != {}".format(localSha1, remoteSha1))
            
        print("sha1 check succeed ({})".format(localSha1))

        
    def getBuiltExes(self):
        return self.configs['builtexes']
        
    def getCopyPlugins(self):
        return self.configs['copyplugins']
    
    def getCopyTranslations(self):
        return self.configs['copytranslations']
    

COMMONCODEHEAD='''// DO NOT EDIT
// This file was created and will be overwritten by distSolution.py
// DO NOT EDIT
'''

CPPCODEHEAD=COMMONCODEHEAD
CPPCODEPREV='''
#ifndef GITREV_INCLUDED_
#define GITREV_INCLUDED_

#include <string>
#include <sstream>
namespace GITREV {
    static constexpr const %(cppchar)s *hashes[][2] =  {

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

CSHARPCODEHEAD = COMMONCODEHEAD

CSHARPCODEPREV = '''
using System.Collections.Generic;
using System.Text;

namespace Ambiesoft {
    static class GitRev
    {
        static Dictionary<string, string> hashes = new Dictionary<string, string>()
        {

'''

CSHARPCODEPOST='''
        };
        public static string GetHashMessage()
        {
            var sb = new StringBuilder();
            foreach(var kv in hashes)
            {
                sb.Append(kv.Key);
                sb.Append(":");
                sb.Append(kv.Value);
                sb.AppendLine();
            }
            return sb.ToString();
        }
    } // class GitRev
}  // namespace GITREV
'''

def createGitRev(gitrev, ShowDummy=False, DummyType='cpp', Char='char'):
    ''' create or change gitrev.h from git hash '''
    if not ShowDummy:
        if not gitrev:
            return
        if not gitrev['gitdirs']:
            exit('"gitdirs" must be specified in "gitrev"')
        if (not 'outheader' in gitrev) and (not 'outtxt' in gitrev) and (not 'outcsharp' in gitrev):
            exit('"outheader", "outcsharp" or "outtxt" must be specified in "gitrev"')
    
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
        namehash.append(['dummy1', '0'*40])
        namehash.append(['dummy2', '0'*40])
    else:
        for gitdir in gitrev['gitdirs']:
            dir = os.path.basename(os.path.abspath(gitdir)).replace('.','').replace('/','').replace('\\','')
            if not dir:
                exit('dir is empty')
            hash = lspy.getGitHash(gitdir, git)
            namehash.append([dir,hash])

    # decide char or wchar
    if not ShowDummy:
        if 'char' in gitrev:
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

    if (gitrev and ('outheader' in gitrev or 'outcsharp' in gitrev)) or (ShowDummy and (DummyType=='cpp' or DummyType=='csharp') ):
        if ShowDummy:
            gitrevheader = sys.stdout;
            if not gitrevheader:
                exit('Failed to open stdout')    
        else:
            if 'outheader' in gitrev and 'outcsharp' in gitrev:
                exit('Both "outheader" and "outcsharp" are specified. Only one of them is allowed.')
            if 'outheader' in gitrev:
                outfile = gitrev['outheader']
                # check extension
                if lspy.getExtension(outfile) != '.h' and lspy.getExtension(outfile) != '.hpp':
                    exit("'outheader specified but its extesnion is wrong. it must be '.h' or '.hpp'")
            elif 'outcsharp' in gitrev:
                outfile = gitrev['outcsharp']
                # check extension
                if lspy.getExtension(outfile) != '.cs':
                    exit("'outheader specified but its extesnion is wrong. it must be '.cs'")
                DummyType='csharp'
            if not outfile:
                exit('No outfile')

            gitrevheader = open(outfile, 'w')
            if not gitrevheader:
                exit('Failed to open', outfile)
        
        if DummyType=='cpp':
            gitrevheader.write(CPPCODEHEAD)
        elif DummyType=='csharp':
            gitrevheader.write(CSHARPCODEHEAD)
        else:
            exit('Unknown DummyType', DummyType)

        insidemap = ''
        for nh in namehash:
            insidemap += '            ' + '{' + literalL + '"' + nh[0] +  '",' + literalL + '"' + nh[1] + '"},\n'

        if DummyType=='cpp':
            codetemplate = CPPCODEPREV + insidemap + CPPCODEPOST
        elif DummyType=='csharp':
            codetemplate = CSHARPCODEPREV + insidemap + CSHARPCODEPOST
        else:
            exit('Unknown DummyType', DummyType)
        
        code = codetemplate % {
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

    if gitrev and 'checkcommitted' in gitrev:
        for gitdir in gitrev['gitdirs']:
            if not lspy.isGitCommited(gitdir, git,Verbose=True):
                exit('"{}" is not comitted'.format(gitdir))
