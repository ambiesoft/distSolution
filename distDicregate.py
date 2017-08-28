import os
from os.path import isfile, isdir
import subprocess
import re

DicregateTotalFileCount = 159

ShouldNotBeFiles = ("conf", "folder.wini", "Register.wini", "fukisokueigo.csv", "kanjiq2s.csv")
ShouldBeFiles = (
    "Ambiesoft.amblib.dll", 
    "Ambiesoft.amblib.pdb", 
    "Ambiesoft.Profile.dll", 
    "cef", 
    "ChromiumFX.dll", 
    "ChromiumFX.pdb", 
    "ChromiumFX.xml", 
    "ChromiumWebBrowser.dll", 
    "ChromiumWebBrowser.pdb", 
    "ChromiumWebBrowser.xml", 
    "crashgate.exe", 
    "crashgate.pdb", 
    "CustomClipboard.dll", 
    "Dicregate.exe", 
    "Dicregate.pdb", 
    "DicregateCfxSub.exe", 
    "DicregateCfxSub.pdb", 
    "DownloadProgressDialog.exe", 
    "DownloadProgressDialog.pdb", 
    "eb.dll", 
    "fakecmd.exe", 
    "fakecmd.pdb", 
    "FolderConfig.exe", 
    "FolderConfig.pdb", 
    "fukisokueigo.csv.zip", 
    "FukisokuWord.dll", 
    "FukisokuWord.pdb", 
    "GetNumericTextDialog.dll", 
    "GetTextDialog.dll", 
    "History.txt", 
    "Images", 
    "ja-JP", 
    "kanjiq2s.csv.zip", 
    "KanjiQ2S.dll", 
    "KanjiQ2S.pdb", 
    "lang", 
    "License.txt", 
    "locale", 
    "MiscUtil.dll", 
    "MiscUtil.pdb", 
    "mshtmlmani.dll", 
    "Readme.txt", 
    "Readme_jp.txt", 
    "RegDicregate.exe", 
    "RegDicregate.pdb", 
    "showballoon.exe", 
    "sqlite3.dll"
    )

ShouldBeOneOfThem = ("libcfx.dll", "libcfx64.dll")

def checkShouldnotExistFile(dicregatedir):
    """ Return false if a file that should not be distributed exists. """
    for f in ShouldNotBeFiles:
        fullpath = dicregatedir + f
        if isfile(fullpath) or isdir(fullpath):
            print(fullpath + " exists.")
            return False
    
    return True
    
def checkShouldBeFiles(dicregatedir):
    for f in ShouldBeFiles:
        fullpath = dicregatedir+f
        if( not (isfile(fullpath) or isdir(fullpath))):
            print(fullpath + " not exists.")
            return False
    
    oneofthem = False
    for f in ShouldBeOneOfThem:
        fullpath = dicregatedir+f
        if(isfile(fullpath)):
            if(oneofthem):
                print(fullpath + " One of them files duplicating.")
                return False
            oneofthem = True
            
    if(not oneofthem):
        print("None of oneofthem files exists.")
        return False
    
    return True
            
def getFileCount(d):
    total = 0
    for _, _, files in os.walk(d):
        total += len(files)
    return total


def work(dicregatedir):
    print("=== Start Testing {} ===".format(dicregatedir))
    
    if not checkShouldnotExistFile(dicregatedir):
        exit(1)
    if not checkShouldBeFiles(dicregatedir):
        exit(1)

    if(DicregateTotalFileCount != getFileCount(dicregatedir)):
        print("{} != {}".format(DicregateTotalFileCount,getFileCount(dicregatedir)))
        exit(1)
    
    print ("Total file count = {}".format(getFileCount(dicregatedir)))    

def getVersionString(dicregateDir):
    """get version string from history.txt"""
    
    fileName = os.path.join(dicregateDir, "history.txt")
    with open(fileName, "r", encoding="utf-8") as f:
        lines = f.readlines()
        line=lines[0]
        m = re.match(r'\d\.\d\.\d\.\d', line)
        return m.group(0)
    
    print("Version not found.")
    exit(1)
    
    
def main():
    targets = (R"C:/Linkout/Dicregate/",R"C:/Linkout/Dicregate64/")
    verstring="";
    for target in targets:
        # check dir
        work(target)
        vstT = getVersionString(target)
        if(verstring and verstring != vstT):
            print("different verstion")
            exit(1)
        verstring = vstT
        
    #archive it
    target = targets[0];
    parentDir = os.path.abspath(os.path.join(target, os.pardir))
    dirName = os.path.basename(os.path.dirname(target))
    archiveexe = os.path.join(parentDir, "{}{}{}".format(dirName,verstring,".exe"));
    
    print("==== creating arhive {} ====".format(archiveexe))
    
    if(os.path.exists(archiveexe)):
        print("{} already exists.".format(archiveexe))
        exit(1)
    
    args = [
        r"C:\LegacyPrograms\7-Zip\7z.exe",
        "a",
        "-sfx7z.sfx",
        archiveexe,
    ]
    
    for t in targets:
        args.append(t)
        
    args.append("-mx9");
    
    print(args)
    subprocess.check_call(args)

        

if __name__ == "__main__":
    main()
    print("Succeeded")
    
    