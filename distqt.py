import sys
import os
import timeit
import subprocess
from shutil import copyfile
from argparse import ArgumentParser
import glob, shutil

QTVER='5.10.0'
TOOL='mingw53_32'

def myexit(message):
    print(message)
    exit(1)

def getQt_obsolete():
    qtdirs = [
        "Y:\\G\\Qt",
        "C:\\local\\Qt",
    ]
    qtdir = ""
    for t in qtdirs:
        if os.path.isdir(t):
            qtdir=t
            break

    if not qtdir:
        myexit("Qt not found")

    return qtdir

def getQtToolBinDir(qtroot):
    # qtDirs = getQt()
    q = os.path.join(qtroot,QTVER)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, TOOL)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, "bin")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def getQmake(qtroot):
    dir =getQtToolBinDir(qtroot)

    qmake = os.path.join(dir, "qmake.exe")
    if not os.path.isfile(qmake):
        myexit("{} is not found.".format(qmake))

    return qmake

def getDeployTool(qtroot):
    dir =getQtToolBinDir(qtroot)

    qmake = os.path.join(dir, "windeployqt.exe")
    if not os.path.isfile(qmake):
        myexit("{} is not found.".format(qmake))

    return qmake

def getLreleaseTool(qtroot):
    dir = getQtToolBinDir(qtroot)
    qmake = os.path.join(dir, "lrelease.exe")
    if not os.path.isfile(qmake):
        myexit("{} is not found.".format(qmake))

    return qmake
    
def getQtPluginDir(qtroot):
    # qtDirs = getQt()
    q = os.path.join(qtroot,QTVER)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, TOOL)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, "plugins")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
        
    return q;
    
def getQtPluginPlatformDir(qtroot):
    q = getQtPluginDir(qtroot)
    q = os.path.join(q, "platforms")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def getQtPluginSqldriversDir(qtroot):
    q = getQtPluginDir(qtroot)
    q = os.path.join(q, "sqldrivers")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def ensureDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        if not os.path.isdir(dir):
            myexit('Could not create {}'.format(dir))

def getBuildToolsBinDir(qtroot):
    cand = [
        "Tools\\mingw530_32\\bin",
    ];
    # qt = getQt();
    
    ret = ""
    for t in cand:
        t = os.path.join(qtroot,t)
        if os.path.isdir(t):
            ret=t
            break

    if not ret:
        myexit("Qt not found")

    return ret

def copyQtFile(distdir, distsubdir, qtdir, qtfile):
    d = os.path.join(distdir, distsubdir)
    ensureDir(d)
    dll = os.path.join(qtdir,qtfile)
    if not os.path.isfile(dll):
        myexit('{} not found.'.format(dll))
    
    dest = os.path.join(d, qtfile)
    copyfile(dll, dest)
    print('copied: {0} => {1}'.format(dll,dest))
    
def main():
    parser = ArgumentParser(
        prog="distqt",
        description="Build Qt Project")

    parser.add_argument(
        "-C",
        nargs='?',
        action="store",
        help="The message string.")
    parser.add_argument(
        "profile",
        nargs='?'
        )
    parser.add_argument(
        "-qtroot",
        nargs='?',
        action="store",
        help="Qt root directory.")
    
    
    args = parser.parse_args()
    if args.C:
        os.chdir(args.C)
        
    pro = args.profile
    if not pro:
        myexit("project file *.pro must be specified.")
    if not os.path.isfile(pro):
        myexit("{} is not a file.".format(pro))
        
    if not os.path.isabs(pro):
        pro = os.path.join('../', pro)
        
    if not os.path.isdir("build"):
        os.mkdir("build")
        if not os.path.isdir("build"):
            myexit("Could not create dir [build]")

    qtroot = args.qtroot
    
    toolbin = getBuildToolsBinDir(qtroot)
    my_env = os.environ.copy()
    my_env["PATH"] = toolbin + os.pathsep + my_env["PATH"]
    os.environ['PATH']=my_env['PATH']
    print("{} is added to path.".format(toolbin))

    os.chdir("build")
    print("Entered directory {}".format(os.getcwd()))

    print("==== creating Makefile ====")
    qmake = getQmake(qtroot)

    args = []
    args.append(qmake)
    args.append(pro)

    print(args)
    subprocess.check_call(args)


    print("==== make ====")
    make = "mingw32-make.exe"

    args=[]
    args.append(make)

    print(args)
    subprocess.check_call(args)


    print("==== deploying ====")
    args=[]
    deploytool = getDeployTool(qtroot)
    releaseexe = "release/SceneExplorer.exe"
    if not os.path.isfile(releaseexe):
        myexit("Release exe {} not found.".format(releaseexe))

    distdir="C:\\Linkout\\SceneExplorer\\"
    ensureDir(distdir)

    args.append(deploytool)
    args.append(releaseexe)
    args.append('--libdir')
    args.append(distdir)
    print(args)
    subprocess.check_call(args)

    copyQtFile(distdir, 'platforms', getQtPluginPlatformDir(qtroot),'qwindows.dll')
    copyQtFile(distdir, 'sqldrivers', getQtPluginSqldriversDir(qtroot), 'qsqlite.dll')
    
       
    dest = os.path.join(distdir,'SceneExplorer.exe')
    copyfile(releaseexe, dest)
    print('copied: {0} => {1}'.format(releaseexe,dest))



    # compile translation-- obsolete ( done in qmake and embedded in resource
    #srctsfiles = glob.iglob(os.path.join('../src/translations', "*.ts"))
    #for file in srctsfiles:
    #    if os.path.isfile(file):
    #        args = []
    #        args.append(getLreleaseTool(qtroot))
    #        args.append(file)
    #        print(args)
    #        subprocess.check_call(args)
    
    # disttransdir = os.path.join(distdir, "translations")
    # ensureDir(disttransdir)
    #
    #srcdistfiles = glob.iglob(os.path.join('../src/translations', "*.qm"))
    #for file in srcdistfiles:
    #    if os.path.isfile(file):
    #        shutil.copy2(file, disttransdir)
            
    
    
    
    
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

