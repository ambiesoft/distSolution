import json
import os
import re
import subprocess
import daver
from easyhash import getSha1
import urllib.request
import time
from funcs import myexit,showDiffAndExit,getAsFullpath,IsRemoteArchiveExists


def getFileCount(d):
    total = 0
    for _, _, files in os.walk(d):
        total += len(files)
    return total


            
class DistConfig:
    def __init__(self, path):
            with open(path,encoding="utf-8") as data_file:
                self.configs = json.load(data_file)
                

                    
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
                if(isfile(fullpath)):
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
        configs = self.configs
        
        fileName = os.path.join(outdir, configs["obtainverfrom"])
        with open(fileName, "r", encoding="utf-8") as f:
            lines = f.readlines()
            line=lines[0]
            regstr = configs["obtainverregex"]
            m = re.search(regstr, line)
            return m.group(0)
        
        myexit("Version not found.")
                            
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
        configs = self.configs
        
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
        
        args.append("-mx9");
        
        print(args)
        subprocess.check_call(args)
        
    def checkAlreadyUploaded(self, verstring):
        """ check remote archive exist and quit if true. """
        configs = self.configs
        
        url = configs['remotedir'] + self.getArchiveName(verstring)
        
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
                remoteSha1 = urllib.request.urlopen(remoteSha1Url).read().decode("utf-8")
                break
            except:
                print("failed {} times to check remote Sha1. Will try again after waiting 5 seconds.".format(loop+1))
                time.sleep(5) # wait 5 seconds
        
        if localSha1.lower() != remoteSha1.lower():
            myexit("sha1 not equal ({} != {}".format(localSha1, remoteSha1))
            
        print("sha1 check succeed ({})".format(localSha1))

        