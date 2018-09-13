import sys
import os
import timeit
import subprocess
from shutil import copyfile
from argparse import ArgumentParser
import glob, shutil
import json
from common import *
from updateBBS import updateBBS

class QtTools:

    def __init__(self, qtVer, qtRoot, qtTool, make):
        self.qtVer = qtVer
        self.qtRoot = qtRoot
        self.qtTool = qtTool
        self.make = make

    def binDir(self):
        q = os.path.join(self.qtRoot, self.qtVer)
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))
        q = os.path.join(q, self.qtTool)
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))
        q = os.path.join(q, "bin")
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))

        return q

#     def buildBinDir(self):
#         ret = os.path.join(self.qtRoot, 'Tools', self.qtBuildTool, 'bin')
#         if not os.path.isdir(ret):
#             myexit("{} is not directory.".format(ret))
# 
#         return ret

    def getMake(self):
        return self.make
    
    def qmake(self):
        dir = self.binDir()
        qmake = os.path.join(dir, "qmake.exe")
        if not os.path.isfile(qmake):
            myexit("{} is not found.".format(qmake))

        return qmake

    def deployTool(self):
        dir = self.binDir()

        windeployqt = os.path.join(dir, "windeployqt.exe")
        if not os.path.isfile(windeployqt):
            myexit("{} is not found.".format(windeployqt))

        return windeployqt

    def pluginDir(self):
        q = os.path.join(self.qtRoot, self.qtVer)
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))
        q = os.path.join(q, self.qtTool)
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))
        q = os.path.join(q, "plugins")
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))

        return q;

    def pluginSubDir(self, dir):
        q = self.pluginDir()
        q = os.path.join(q, dir)
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))

        return q




                
                
                
def myexit(message):
    print(message)
    exit(1)

# def getLreleaseTool(qtroot):
#    dir = getQtToolBinDir(qtroot)
#    qmake = os.path.join(dir, "lrelease.exe")
#    if not os.path.isfile(qmake):
#        myexit("{} is not found.".format(qmake))

#    return qmake


def ensureDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)
        if not os.path.isdir(dir):
            myexit('Could not create {}'.format(dir))


def copyQtFile(distdir, distsubdir, qtdir, qtfile):
    d = os.path.join(distdir, distsubdir)
    ensureDir(d)
    dll = os.path.join(qtdir, qtfile)
    if not os.path.isfile(dll):
        myexit('{} not found.'.format(dll))
    
    dest = os.path.join(d, qtfile)
    copyfile(dll, dest)
    print('copied: {0} => {1}'.format(dll, dest))

    
def main():
    parser = ArgumentParser(
        prog="distqt",
        description="Build Qt Project")

    parser.add_argument(
        "-C",
        nargs='?',
        action="store",
        help="Set current directory.")
    parser.add_argument(
        "profile",
        nargs='?'
        )
    parser.add_argument(
        "-qtroot",
        nargs=1,
        action="store",
        type=str,
        help="Qt root directory.")
    parser.add_argument(
        "-qtversion",
        nargs=1,
        action='store',
        help="Qt Version (like 5.10.1)")
    parser.add_argument(
        "-qtversiontools",
        nargs=1,
        action='store',
        help="Qt Version-tools (like mingw53_32)")
    parser.add_argument(
         "-make",
         nargs=1,
         action='store',
         help="path to 'make' or 'msbuild'")
    parser.add_argument(
        "-distfile",
        nargs=1,
        action='store',
        help="distfile")
    parser.add_argument(
        "-path",
        nargs=1,
        action='store',
        help="set to path")
    parser.add_argument(
        "-distdir",
        nargs=1,
        action='store',
        help="distdir")
    
    args = parser.parse_args()
    
    if args.C:
        os.chdir(args.C)
        
    if args.path:
        for p in args.path:
            my_env = os.environ.copy()
            my_env["PATH"] = p + os.pathsep + my_env["PATH"]
            os.environ['PATH'] = my_env['PATH']
            print("{} is added to path.".format(p))
             
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

    
    distdir = args.distdir[0]
    if not distdir:
        myexit("-distdir must not be empty.")
    if not os.path.isdir(distdir):
        os.mkdir(distdir)
        if not os.path.isdir(distdir):
            myexit("'{}' is not a directory.".format(distdir))
        
    
    
    qtTools = QtTools(args.qtversion[0], args.qtroot[0], args.qtversiontools[0], args.make[0])
    distconfig = DistConfig(args.distfile[0])


    
#     buildtoolbin = qtTools.buildBinDir()
#     my_env = os.environ.copy()
#     my_env["PATH"] = buildtoolbin + os.pathsep + my_env["PATH"]
#     os.environ['PATH'] = my_env['PATH']
#     print("{} is added to path.".format(buildtoolbin))

    os.chdir("build")
    print("Entered directory {}".format(os.getcwd()))

    print("==== creating Makefile ====")
    qmake = qtTools.qmake()  # getQmake(qtroot)

    args = []
    args.append(qmake)
    args.append(pro)

    print(args)
    subprocess.check_call(args)

    print("==== make ====")
    make = qtTools.getMake() # "mingw32-make.exe"

    args = []
    args.append(make)

    print(args)
    subprocess.check_call(args)

    # print("==== Check version ====")
    
    ensureDir(distdir)

    print("==== deploying ====")
    args = []
    deploytool = qtTools.deployTool()  # getDeployTool(qtroot)
    releaseexe = "release/{}.exe".format(distconfig.getProjectName())
    if not os.path.isfile(releaseexe):
        myexit("Release exe {} not found.".format(releaseexe))


    args.append(deploytool)
    args.append(releaseexe)
    args.append('--libdir')
    args.append(distdir)
    print(args)
    subprocess.check_call(args)

    copyQtFile(distdir, 'platforms', qtTools.pluginSubDir('platforms'), 'qwindows.dll')
    copyQtFile(distdir, 'sqldrivers', qtTools.pluginSubDir('sqldrivers'), 'qsqlite.dll')
    copyQtFile(distdir, 'imageformats', qtTools.pluginSubDir('imageformats'), 'qjpeg.dll')
       
    dest = os.path.join(distdir, '{}.exe'.format(distconfig.getProjectName()))
    copyfile(releaseexe, dest)
    print('copied: {0} => {1}'.format(releaseexe, dest))

    
    # dist check
    print("==== check files ====")
    distconfig.checkTarget(distdir)



    verstr = distconfig.getVersionString(distdir)


    print("==== creating archive ====")
    print('version is {0}'.format(verstr))
    distconfig.checkAlreadyUploaded(verstr)
    distconfig.createArchive(r"C:\LegacyPrograms\7-Zip\7z.exe", distdir, verstr)
        

    print("==== uploading archive ====")
    distconfig.upload()
    

    ## update BBS
    print("==== Updating BBS... ====")
    print(updateBBS( distconfig.getProjectName(), 
                     verstr, 
                     distconfig.getRemoteDir() + distconfig.getArchiveName(verstr),
                     distconfig.getChangeLong(distdir)))

    
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
