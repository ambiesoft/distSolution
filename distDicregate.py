import os
from os.path import isfile, isdir
from test.test_decimal import file

DicregateTotalFileCount = 159

ShouldNotBeFiles = ("folder.wini", "Register.wini", "fukisokueigo.csv", "kanjiq2s.csv")
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
    for file in ShouldNotBeFiles:
        fullpath = dicregatedir + file
        if isfile(fullpath) or isdir(fullpath):
            print(fullpath + " exists.")
            return False
    
    return True
    
def checkShouldBeFiles(dicregatedir):
    for file in ShouldBeFiles:
        fullpath = dicregatedir+file
        if( not (isfile(fullpath) or isdir(fullpath))):
            print(fullpath + " not exists.")
            return False
    
    oneofthem = False
    for file in ShouldBeOneOfThem:
        fullpath = dicregatedir+file
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
    print("OK");

def main():
    work(R"C:/Linkout/Dicregate/")
    work(R"C:/Linkout/Dicregate64/")
    
if __name__ == "__main__":
    main()
    
    