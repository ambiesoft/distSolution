import sys
import os
import timeit
import subprocess
from shutil import copyfile
from argparse import ArgumentParser
import glob, shutil


class QtTools:

    def __init__(self, qtVer, qtRoot, qtTool, qtBuildTool):
        self.qtVer = qtVer
        self.qtRoot = qtRoot
        self.qtTool = qtTool
        self.qtBuildTool = qtBuildTool

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

    def buildBinDir(self):
        # cand = [
        #    "Tools\\mingw530_32\\bin",
        # ];
        # qt = getQt();

        ret = os.path.join(self.qtRoot, 'Tools', self.qtBuildTool, 'bin')
        if not os.path.isdir(ret):
            myexit("{} is not directory.".format(ret))

        return ret

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

    def pluginPlatformDir(self):
        q = self.pluginDir()
        q = os.path.join(q, "platforms")
        if not os.path.isdir(q):
            myexit("{} is not found.".format(q))

        return q

    def pluginSqldriversDir(self):
        q = self.pluginDir()
        q = os.path.join(q, "sqldrivers")
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
        help="The message string.")
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
        "-qttools",
        nargs=1,
        action='store',
        help="Qt Tools (like mingw530_32)")
    
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

    

    qtTools = QtTools(args.qtversion[0], args.qtroot[0], args.qtversiontools[0], args.qttools[0])

    buildtoolbin = qtTools.buildBinDir()

    my_env = os.environ.copy()
    my_env["PATH"] = buildtoolbin + os.pathsep + my_env["PATH"]
    os.environ['PATH'] = my_env['PATH']
    print("{} is added to path.".format(buildtoolbin))

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
    make = "mingw32-make.exe"

    args = []
    args.append(make)

    print(args)
    subprocess.check_call(args)

    # print("==== Check version ====")
    distdir = "C:\\Linkout\\SceneExplorer\\"
    ensureDir(distdir)

    print("==== deploying ====")
    args = []
    deploytool = qtTools.deployTool()  # getDeployTool(qtroot)
    releaseexe = "release/SceneExplorer.exe"
    if not os.path.isfile(releaseexe):
        myexit("Release exe {} not found.".format(releaseexe))


    args.append(deploytool)
    args.append(releaseexe)
    args.append('--libdir')
    args.append(distdir)
    print(args)
    subprocess.check_call(args)

    # copyQtFile(distdir, 'platforms', getQtPluginPlatformDir(qtroot),'qwindows.dll')
    copyQtFile(distdir, 'platforms', qtTools.pluginPlatformDir(), 'qwindows.dll')
    # copyQtFile(distdir, 'sqldrivers', getQtPluginSqldriversDir(qtroot), 'qsqlite.dll')
    copyQtFile(distdir, 'sqldrivers', qtTools.pluginSqldriversDir(), 'qsqlite.dll')
       
    dest = os.path.join(distdir, 'SceneExplorer.exe')
    copyfile(releaseexe, dest)
    print('copied: {0} => {1}'.format(releaseexe, dest))

    # compile translation-- obsolete ( done in qmake and embedded in resource
    # srctsfiles = glob.iglob(os.path.join('../src/translations', "*.ts"))
    # for file in srctsfiles:
    #    if os.path.isfile(file):
    #        args = []
    #        args.append(getLreleaseTool(qtroot))
    #        args.append(file)
    #        print(args)
    #        subprocess.check_call(args)
    
    # disttransdir = os.path.join(distdir, "translations")
    # ensureDir(disttransdir)
    #
    # srcdistfiles = glob.iglob(os.path.join('../src/translations', "*.qm"))
    # for file in srcdistfiles:
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
