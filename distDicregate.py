import sys
import os
from os.path import isfile, isdir
import subprocess
import re
from os import getenv
import timeit

APPNAME = 'distDicregate'
VERSION = '1.0';
APPDISC = 'check files and archive them'

DicregateTotalFileCount = 159

ShouldNotBeFiles = ("conf", "folder.wini", "Register.wini", "fukisokueigo.csv", "kanjiq2s.csv")
ShouldBeFiles = (
    'Ambiesoft.amblib.dll',
    'Ambiesoft.amblib.pdb',
    'Ambiesoft.Profile.dll',
    'cef/chrome_elf.dll',
    'cef/d3dcompiler_43.dll',
    'cef/d3dcompiler_47.dll',
    'cef/icudtl.dat',
    'cef/libcef.dll',
    'cef/libEGL.dll',
    'cef/libGLESv2.dll',
    'cef/natives_blob.bin',
    'cef/Resources/cef.pak',
    'cef/Resources/cef_100_percent.pak',
    'cef/Resources/cef_200_percent.pak',
    'cef/Resources/cef_extensions.pak',
    'cef/Resources/devtools_resources.pak',
    'cef/Resources/locales/am.pak',
    'cef/Resources/locales/ar.pak',
    'cef/Resources/locales/bg.pak',
    'cef/Resources/locales/bn.pak',
    'cef/Resources/locales/ca.pak',
    'cef/Resources/locales/cs.pak',
    'cef/Resources/locales/da.pak',
    'cef/Resources/locales/de.pak',
    'cef/Resources/locales/el.pak',
    'cef/Resources/locales/en-GB.pak',
    'cef/Resources/locales/en-US.pak',
    'cef/Resources/locales/es-419.pak',
    'cef/Resources/locales/es.pak',
    'cef/Resources/locales/et.pak',
    'cef/Resources/locales/fa.pak',
    'cef/Resources/locales/fi.pak',
    'cef/Resources/locales/fil.pak',
    'cef/Resources/locales/fr.pak',
    'cef/Resources/locales/gu.pak',
    'cef/Resources/locales/he.pak',
    'cef/Resources/locales/hi.pak',
    'cef/Resources/locales/hr.pak',
    'cef/Resources/locales/hu.pak',
    'cef/Resources/locales/id.pak',
    'cef/Resources/locales/it.pak',
    'cef/Resources/locales/ja.pak',
    'cef/Resources/locales/kn.pak',
    'cef/Resources/locales/ko.pak',
    'cef/Resources/locales/lt.pak',
    'cef/Resources/locales/lv.pak',
    'cef/Resources/locales/ml.pak',
    'cef/Resources/locales/mr.pak',
    'cef/Resources/locales/ms.pak',
    'cef/Resources/locales/nb.pak',
    'cef/Resources/locales/nl.pak',
    'cef/Resources/locales/pl.pak',
    'cef/Resources/locales/pt-BR.pak',
    'cef/Resources/locales/pt-PT.pak',
    'cef/Resources/locales/ro.pak',
    'cef/Resources/locales/ru.pak',
    'cef/Resources/locales/sk.pak',
    'cef/Resources/locales/sl.pak',
    'cef/Resources/locales/sr.pak',
    'cef/Resources/locales/sv.pak',
    'cef/Resources/locales/sw.pak',
    'cef/Resources/locales/ta.pak',
    'cef/Resources/locales/te.pak',
    'cef/Resources/locales/th.pak',
    'cef/Resources/locales/tr.pak',
    'cef/Resources/locales/uk.pak',
    'cef/Resources/locales/vi.pak',
    'cef/Resources/locales/zh-CN.pak',
    'cef/Resources/locales/zh-TW.pak',
    'cef/snapshot_blob.bin',
    'cef/widevinecdmadapter.dll',
    'ChromiumFX.dll',
    'ChromiumFX.pdb',
    'ChromiumFX.xml',
    'ChromiumWebBrowser.dll',
    'ChromiumWebBrowser.pdb',
    'ChromiumWebBrowser.xml',
    'crashgate.exe',
    'crashgate.pdb',
    'CustomClipboard.dll',
    'Dicregate.exe',
    'Dicregate.pdb',
    'DicregateCfxSub.exe',
    'DicregateCfxSub.pdb',
    'DownloadProgressDialog.exe',
    'DownloadProgressDialog.pdb',
    'eb.dll',
    'fakecmd.exe',
    'fakecmd.pdb',
    'FolderConfig.exe',
    'FolderConfig.pdb',
    'fukisokueigo.csv.zip',
    'FukisokuWord.dll',
    'FukisokuWord.pdb',
    'GetNumericTextDialog.dll',
    'GetTextDialog.dll',
    'History.txt',
    'Images/Default/app.bmp',
    'Images/Default/app.ico',
    'Images/Default/HistToolImage_Sort.bmp',
    'Images/Default/HistToolImage_ToBottom.bmp',
    'Images/Default/HistToolImage_ToTop.bmp',
    'Images/Default/InfoProvider.ico',
    'Images/Default/ListToolImage_NextDic.bmp',
    'Images/Default/ListToolImage_NextItem.bmp',
    'Images/Default/ListToolImage_PrevDic.bmp',
    'Images/Default/ListToolImage_PrevItem.bmp',
    'Images/Default/ListToolImage_Stop.bmp',
    'Images/Default/StatusDicImage_Epwing.bmp',
    'Images/Default/StatusDicImage_Internet.bmp',
    'Images/Default/StatusImage_NextPage.bmp',
    'Images/Default/StatusImage_PrevPage.bmp',
    'Images/Default/TabImage_Done.bmp',
    'Images/Default/TabImage_Down.bmp',
    'Images/Default/TabImage_Filtered.bmp',
    'Images/Default/TabImage_Locked.bmp',
    'Images/Default/TabImage_NotFound.bmp',
    'Images/Default/TabImage_Ready.bmp',
    'Images/Default/TabImage_SearchError.bmp',
    'Images/Default/ToolImage_Back.bmp',
    'Images/Default/ToolImage_FindDown.bmp',
    'Images/Default/ToolImage_FindUp.bmp',
    'Images/Default/ToolImage_Forward.bmp',
    'Images/Default/ToolImage_Highlight.bmp',
    'Images/Default/ToolImage_Refresh.bmp',
    'Images/Default/ToolImage_Search.bmp',
    'Images/Default/ToolImage_Stop.bmp',
    'Images/Default/ToolImage_TabBack.bmp',
    'Images/Default/ToolImage_TabForward.bmp',
    'Images/Default/win.ico',
    'Images/Default/WinToolImage_Back.bmp',
    'Images/Default/WinToolImage_FindDown.bmp',
    'Images/Default/WinToolImage_FindUp.bmp',
    'Images/Default/WinToolImage_Forward.bmp',
    'Images/Default/WinToolImage_Highlight.bmp',
    'Images/Default/WinToolImage_Refresh.bmp',
    'Images/Default/WinToolImage_Stop.bmp',
    'Images/Default/WinToolImage_Window.bmp',
    'ja-JP/Dicregate.resources.dll',
    'ja-JP/FolderConfig.resources.dll',
    'ja-JP/GetNumericTextDialog.resources.dll',
    'ja-JP/GetTextDialog.resources.dll',
    'ja-JP/RegDicregate.resources.dll',
    'kanjiq2s.csv.zip',
    'KanjiQ2S.dll',
    'KanjiQ2S.pdb',
    'lang/DownloadProgressDialog.jpn.txt',
    'License.txt',
    'locale/Japanese/LC_MESSAGES/eb.mo',
    'MiscUtil.dll',
    'MiscUtil.pdb',
    'mshtmlmani.dll',
    'Readme.txt',
    'Readme_jp.txt',
    'RegDicregate.exe',
    'RegDicregate.pdb',
    'showballoon.exe',
    'sqlite3.dll',
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
        if( not (isfile(fullpath))):
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


def work(target):
    dicregatedir = target['outdir'];
    print("=== Start Testing {} ===".format(dicregatedir))
    
    if not checkShouldnotExistFile(dicregatedir):
        myexit(1)
    if not checkShouldBeFiles(dicregatedir):
        myexit(1)

    if(DicregateTotalFileCount != getFileCount(dicregatedir)):
        print("{} != {}".format(DicregateTotalFileCount,getFileCount(dicregatedir)))
        myexit(1)
    
    print ("Total file count = {}".format(getFileCount(dicregatedir)))    

def getVersionString(target):
    """get version string from history.txt"""
    
    dicregatedir = target['outdir'];
    
    fileName = os.path.join(dicregatedir, "history.txt")
    with open(fileName, "r", encoding="utf-8") as f:
        lines = f.readlines()
        line=lines[0]
        m = re.search(r'\d\.\d\.\d\.\d', line)
        return m.group(0)
    
    print("Version not found.")
    myexit(1)
    
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

def build(target):
    """build dicregate"""
    msbuildexe = getMsBuildExe()
    if not msbuildexe:
        print("MSBuild.exe not found.")
        myexit(1)
        
     

    args = [
        msbuildexe,
        target['solutionfile'],
        "/t:zzzDistResource",
        "/p:Configuration=zzzDist",
        "/p:Platform={}".format(target["platform"])
    ]
     
    print(args)
    subprocess.check_call(args)
    
def main():
    if sys.version_info[0] < 3:
        print("Please use python3")
        print (sys.version)
        myexit(1)
        
    print('{} {} ({})'.format(APPNAME,VERSION,APPDISC))
    
    if len(sys.argv) > 1:
        solutiondir = sys.argv[1]
    else: 
        solutiondir = os.path.join(os.path.dirname(os.path.realpath(__file__)), R"../Dicregate\trunk\Dicregate")
        
    solutionfile = os.path.join(solutiondir, "Dicregate2013.sln")
        
    if not isfile(solutionfile):
        print("solution file not found")
        myexit(1)
    
    targets = (
            { 
                "solutiondir":solutiondir,
                "solutionfile":solutionfile,
                "outdir" : R"C:/Linkout/Dicregate/",
                "platform":"Win32"
            },

              
            {
                "solutiondir":solutiondir,
                "solutionfile":solutionfile,
                "outdir" : R"C:/Linkout/Dicregate64/",
                "platform":"x64"
            }
    )
    verstring="";
    for target in targets:
        # build
        build(target)
        # check dir
        work(target)
        vstT = getVersionString(target)
        if(verstring and verstring != vstT):
            print("different verstion")
            myexit(1)
        verstring = vstT
        
    #archive it
    target = targets[0];
    outdir=target['outdir']
    parentDir = os.path.abspath(os.path.join(outdir, os.pardir))
    dirName = os.path.basename(os.path.dirname(outdir))
    archiveexe = os.path.join(parentDir, "{}{}{}".format(dirName,verstring,".exe"));
    
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
    
    for t in targets:
        args.append(t['outdir'])
        
    args.append("-mx9");
    
    print(args)
    subprocess.check_call(args)

        
def myexit(retval):
    input('Press ENTER to exit')
    exit(retval)
    
if __name__ == "__main__":
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    
    print("Succeeded ({} sec)".format(stop-start))
    input('Press ENTER to exit')
    
