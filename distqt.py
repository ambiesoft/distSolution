import sys
import os
import timeit
import subprocess
from shutil import copyfile
from argparse import ArgumentParser

QTVER='5.10.0'
TOOL='mingw53_32'

def myexit(message):
    print(message)
    exit(1)

def getQt():
    qtdirs = [
        "Y:\\local\\Qt",
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

def getQtToolBinDir():
    qtDirs = getQt()
    q = os.path.join(qtDirs,QTVER)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, TOOL)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, "bin")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def getQmake():
    dir =getQtToolBinDir()

    qmake = os.path.join(dir, "qmake.exe")
    if not os.path.isfile(qmake):
        myexit("{} is not found.".format(qmake))

    return qmake

def getDeployTool():
    dir =getQtToolBinDir()

    qmake = os.path.join(dir, "windeployqt.exe")
    if not os.path.isfile(qmake):
        myexit("{} is not found.".format(qmake))

    return qmake


def getQtPluginDir():
    qtDirs = getQt()
    q = os.path.join(qtDirs,QTVER)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, TOOL)
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
    q = os.path.join(q, "plugins")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))
        
    return q;
    
def getQtPluginPlatformDir():
    q = getQtPluginDir()
    q = os.path.join(q, "platforms")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def getQtPluginSqldriversDir():
    q = getQtPluginDir()
    q = os.path.join(q, "sqldrivers")
    if not os.path.isdir(q):
        myexit("{} is not found.".format(q))

    return q

def ensureDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        if not os.path.isdir(dir):
            myexit('Could not create {}'.format(dir))

def getBuildToolsBinDir():
    cand = [
        "C:\\local\\Qt\\Tools\\mingw530_32\\bin",
        "Y:\\local\\Qt\\Tools\\mingw530_32\\bin",
    ];
    ret = ""
    for t in cand:
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
    copyfile(dll, os.path.join(d,qtfile))
    
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

    toolbin = getBuildToolsBinDir()
    my_env = os.environ.copy()
    my_env["PATH"] = toolbin + os.pathsep + my_env["PATH"]
    os.environ['PATH']=my_env['PATH']
    print("{} is added to path.".format(toolbin))

    os.chdir("build")
    print("Entered directory {}".format(os.getcwd()))

    print("==== creating Makefile ====")
    qmake = getQmake()

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
    deploytool = getDeployTool()
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

    copyQtFile(distdir, 'platforms', getQtPluginPlatformDir(),'qwindows.dll')
    copyQtFile(distdir, 'sqldrivers', getQtPluginSqldriversDir(), 'qsqlite.dll')
    
       

    copyfile(releaseexe, os.path.join(distdir,'SceneExplorer.exe'))
    
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

