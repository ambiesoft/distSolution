import json
import os
import re
import subprocess

def myexit(s):
    print(s)
    exit(1)

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
    
        if(configs['TotalFileCount'] != getFileCount(outdir)):
            myexit("TotalFileCount different. ({} != {})".format(configs['TotalFileCount'], getFileCount(outdir)))
    
        print ("Total file count = {}".format(getFileCount(outdir)))   
        
    def createArchive(self, path7z, targetdir, verstring):
        configs = self.configs
        
        archiveexe = "{}-{}{}".format(configs["name"], verstring, ".exe")
        archiveexefull = os.path.join(configs["archivedir"], archiveexe)
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
        