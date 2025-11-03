import preinstall
import sys
import os
from os.path import isfile, isdir
import subprocess
import re
from os import getenv
import timeit
import glob
import json
import urllib.request
import time
from argparse import ArgumentParser
import daver
from easyhash import getSha1
from updateBBS import updateBBS
from funcs import getAsFullpath, getPathDiffs, getFileListAsFullPath, myexit, showDiffAndExit, IsRemoteArchiveExists, getChangeLog, getFileCount
from collections import Counter
import inspect
import certifi

from lsPy import lspy
import common

APPNAME = 'distSolution'
VERSION = '1.2.5'
APPDISC = 'build, check files, archive them and distribute solution'

# global config
configs = {}


def checkShouldnotExistFile(distDir, shouldnot):
    """ Return false if a file that should not be distributed exists. """
    for f in shouldnot:
        fullpath = os.path.join(distDir, f)
        if isfile(fullpath) or isdir(fullpath):
            myexit(fullpath + " exists.")
            return False

    return True


def checkShouldBeFiles(distDir, shouldbe):
    for f in shouldbe:
        fullpath = os.path.join(distDir, f)
        if (not (isfile(fullpath))):
            myexit(fullpath + " not exists.")
            return False

    return True


def checkShouldOneOfFiles(distDir, shouldone):
    if shouldone:
        oneofthem = False
        for f in shouldone:
            fullpath = distDir+f
            if (isfile(fullpath)):
                if (oneofthem):
                    myexit(fullpath + " One of them files duplicating.")
                    return False
                oneofthem = True

        if (not oneofthem):
            myexit("None of oneofthem files exists.")
            return False

    return True


def checkFileCount(sbf, outdir):
    shouldBeFull = getAsFullpath(sbf, outdir)

    if (('TotalFileCount' not in configs) or configs['TotalFileCount'] == "exact"):
        showDiffAndExit(outdir, shouldBeFull, configs['TotalFileCount'], True)
    elif (isinstance(configs['TotalFileCount'], int)):
        if (configs['TotalFileCount'] != getFileCount(outdir)):
            showDiffAndExit(outdir, shouldBeFull,
                            configs['TotalFileCount'], False)
    else:
        myexit("[TotalFileCount] must be int or 'exact'")

    print("Total file count = {}".format(getFileCount(outdir)))


def checkTarget(target):
    global configs

    outdir = target['outdir']
    print("=== Start Testing {} ===".format(outdir))

    if "ShouldNotBeFiles" in configs:
        checkShouldnotExistFile(outdir, configs["ShouldNotBeFiles"])

    if "ShouldBeFiles" in configs:
        sbf = configs["ShouldBeFiles"]
        checkShouldBeFiles(outdir, sbf)
        checkFileCount(sbf, outdir)
    if "ShouldBeFiles" in target:
        sbf = target["ShouldBeFiles"]
        checkShouldBeFiles(outdir, sbf)
        checkFileCount(sbf, outdir)

    if "ShouldBeOneOfThem" in configs:
        checkShouldOneOfFiles(outdir, configs["ShouldBeOneOfThem"])


def getVersionString(target):
    """get version string from history.txt"""
    global configs

    outdir = target['outdir']

    fileName = os.path.join(outdir, configs["obtainverfrom"])
    with open(fileName, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
        for line in lines:
            regstr = configs["obtainverregex"]
            m = re.search(regstr, line)
            if (m):
                return m.group(0)

    myexit("Version not found.")


def getMsBuildExe2(pf, vsvar):
    if pf:
        if vsvar == 12:
            pf = os.path.join(pf, R"MSBuild\12.0\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
        elif vsvar == 15:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
        elif vsvar == 16:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio\2019\Community\MSBuild\Current\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
        elif vsvar == 17:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe")
            if isfile(pf):
                return pf
    return None


def getDevenvExeOrComInner(pf, vsvar, ext):
    if pf:
        if vsvar == 12:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio 12.0\Common7\IDE\devenv" + ext)
            if isfile(pf):
                return pf
        # elif vsvar==15:
        #     pf = os.path.join(pf, R"Microsoft Visual Studio\2017\Community\MSBuild\15.0\Bin\MSBuild.exe")
        #     if isfile(pf):
        #         return pf
        elif vsvar == 16:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio\2019\Community\Common7\IDE\devenv" + ext)
            if isfile(pf):
                return pf
        elif vsvar == 17:
            pf = os.path.join(
                pf, R"Microsoft Visual Studio\2022\Community\Common7\IDE\devenv" + ext)
            if isfile(pf):
                return pf
    return None


def getVsVerFromSln(sln):
    vsvar = 0
    # Get VS version from solution file
    with open(sln, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
        for line in lines:
            vsvermatch = re.search(
                'VisualStudioVersion\\s=\\s(?P<topver>\\d+)', line)
            if not vsvermatch:
                continue
            topver = int(vsvermatch.group('topver'))
            if topver == 12:
                print("solution is for Visual Studio 12")
                vsvar = 12
                break
            elif topver == 15:
                print("solution is for Visual Studio 15")
                vsvar = 15
                break
            elif topver == 16:
                print("solution is for Visual Studio 2019")
                vsvar = 16
                break
            elif topver == 17:
                print("solution is for Visual Studio 2022")
                vsvar = 17
                break
    return vsvar


def getMsBuildExe(solution):
    vsvar = getVsVerFromSln(solution)

    if not vsvar:
        myexit('Could not find VS version from solution')

    pf = getMsBuildExe2(getenv("ProgramFiles"), vsvar)
    if pf and isfile(pf):
        return pf

    pf = getMsBuildExe2(getenv("ProgramFiles(x86)"), vsvar)
    if pf and isfile(pf):
        return pf

    return None


def getDevenvExeOrCom(solution, ext='.com'):
    vsvar = getVsVerFromSln(solution)

    if not vsvar:
        myexit('Could not find VS version from solution')

    pf = getDevenvExeOrComInner(getenv("ProgramFiles"), vsvar, ext)
    if pf and isfile(pf):
        return pf

    pf = getDevenvExeOrComInner(getenv("ProgramFiles(x86)"), vsvar, ext)
    if pf and isfile(pf):
        return pf

    return None


def buildwithMSBuild(solution, target):
    """build target of solution"""

    nugetRestore(solution)

    global configs

    msbuildexe = getMsBuildExe(solution)
    if not msbuildexe:
        myexit("MSBuild.exe not found.")

    args = [
        msbuildexe,
        solution,
        #        "/t:zzzDistResource",
        #        "/p:Configuration=zzzDist",
        #        "/p:Platform={}".format(target["platform"])
    ]

    if "platform" in target:
        args.append("/p:platform={}".format(target["platform"]))

    if "setoutdirforbuild" in target and target["setoutdirforbuild"]:
        outDirBuild = os.path.abspath(target["outdir"])
        # will add the trailing slash if it's not already there.
        outDirBuild = os.path.join(outDirBuild, '')
        args.append('/p:outdir={}'.format(outDirBuild))

    if "targetproject" in configs:
        args.append("/t:{}".format(configs["targetproject"]))

    if "configuration" in configs:
        args.append("/p:Configuration={}".format(configs["configuration"]))

    print(args)
    subprocess.check_call(args)


def nugetRestore(solution):
    """ restore nuget packages """
    msbuildexe = getMsBuildExe(solution)
    if not msbuildexe:
        myexit("MSBuild.exe not found.")

    args = [
        msbuildexe,
        solution,
        "/t:Restore"
    ]

    print(args)
    subprocess.check_call(args)


def buildwithDEVENV(solution, target):
    """build target of solution"""
    global configs

    nugetRestore(solution)

    devenvexe = getDevenvExeOrCom(solution)
    if not devenvexe:
        myexit("devenv.exe not found.")

    args = [
        devenvexe,
        solution,
        # '/build', 'zzzDist|Win32',
        # '/project', 'zzzDistResource'
    ]

    if "configuration" in configs:
        args.append('/build')
        arg = configs["configuration"]
        if "platform" in target:
            arg = arg + '|' + target["platform"]
        args.append(arg)

    if "setoutdirforbuild" in target and target["setoutdirforbuild"]:
        myexit("'outdir' is no supported in devenv build.")

    if "targetproject" in configs:
        args.append('/project')
        args.append(configs["targetproject"])

    print(args)
    subprocess.check_call(args)


def checkArchivingDir(archivingfull, outdirsfull):
    ''' archivingfull must constans dirs only '''
    # traverse root directory, and list directories as dirs and files as files
    dirs = os.listdir(archivingfull)
    dirsfull = [os.path.join(archivingfull, dir) for dir in dirs]
    # compare efficiently
    if Counter(dirsfull) != Counter(outdirsfull):
        myexit('archivingdir is not equal to outdirs')


def main():
    if sys.version_info[0] < 3:
        exit("Please use python3" + sys.version)

    # print('{} {} ({})'.format(APPNAME,VERSION,APPDISC))

    parser = ArgumentParser(
        prog="distSolution",
        description="Build, archive and distribute Visual Studio solution")

    parser.add_argument(
        "-C",
        nargs='?',
        action="store",
        help="Set current directory.")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="skip build process"
    )
    parser.add_argument(
        "--skip-check",
        action="store_true",
        help="skip check process"
    )
    parser.add_argument(
        "--skip-archive",
        action="store_true",
        help="skip archive process"
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="skip upload process"
    )
    parser.add_argument(
        "--skip-hashcheck",
        action="store_true",
        help="skip hashcheck process"
    )
    parser.add_argument(
        "--skip-bbs",
        action="store_true",
        help="skip bbs process"
    )
    parser.add_argument(
        "--show-dummygitrev",
        action="store_true",
        help="show c++ gitrev code in char. This can be use for temporary output."
    )
    parser.add_argument(
        "--show-dummygitrev-wchar",
        action="store_true",
        help="show c++ gitrev code in wchar_t. This can be use for temporary output."
    )
    parser.add_argument(
        "--show-dummygitrev-csharp",
        action="store_true",
        help="show c# gitrev code. This can be use for temporary output."
    )
    parser.add_argument(
        "--show-dummygitrev-txt",
        action="store_true",
        help="show gitrev text. This can be use for the first dummy output."
    )
    parser.add_argument('inputfile',
                        nargs='?')

    parser.add_argument(
        "--currentdir-sameasdist",
        action="store_true",
        help="Set current directory as the same directory of input file"
    )

    commandargs = parser.parse_args()

    if commandargs.C and commandargs.currentdir_sameasdist:
        exit("'-C' and '--currentdir-sameasdist' is exclusive")
    if commandargs.C:
        print("Setting current directory to '{}'".format(commandargs.C))
        os.chdir(commandargs.C)
    if commandargs.currentdir_sameasdist:
        if not commandargs.inputfile:
            exit("No input file. It is needed by '--currentdir-sameasdist'")
        if not os.path.isabs(commandargs.inputfile):
            exit(
                "Input file is not absolute path. It must be absolute path to set current directory")
        dir = os.path.dirname(commandargs.inputfile)
        print("Setting current directory to '{}'".format(dir))
        os.chdir(dir)
    if commandargs.show_dummygitrev_wchar:
        common.createGitRev(None, ShowDummy=True, Char='wchar')
        exit(0)
    if commandargs.show_dummygitrev:
        common.createGitRev(None, ShowDummy=True)
        exit(0)
    if commandargs.show_dummygitrev_csharp:
        common.createGitRev(None, ShowDummy=True, DummyType='csharp')
        exit(0)
    if commandargs.show_dummygitrev_txt:
        common.createGitRev(None, ShowDummy=True, DummyType='txt')
        exit(0)

    global configs

    if sys.stdin.isatty():
        if not commandargs.inputfile:
            exit('No input input file')
        distFile = commandargs.inputfile
        filetype = lspy.getInputfileType(distFile)
        print("Opening input {} as {}".format(distFile, filetype))
        with open(distFile, encoding="utf-8-sig") as data_file:
            if filetype == 'yaml':
                preinstall.importWithInstall('pyyaml', True)
                import yaml
                configs = yaml.safe_load(data_file)
            else:
                configs = json.load(data_file)
    else:
        # read from pipe
        configs = json.load(sys.stdin)

    # create gitrev.h if specified
    if 'gitrev' in configs:
        common.createGitRev(configs['gitrev'])

    if not 'solution' in configs:
        exit('"solution" is not specifed')

    solutionFile = os.path.join(os.path.dirname(distFile), configs["solution"])
    verstring = ""

    # build first
    if not commandargs.skip_build:
        for target in configs['targets']:
            if 'builder' in configs and configs['builder'] == 'devenv':
                buildwithDEVENV(solutionFile, target)
            else:
                buildwithMSBuild(solutionFile, target)

    # check
    for target in configs['targets']:
        if not commandargs.skip_check:
            checkTarget(target)
        vstT = getVersionString(target)
        if (verstring and verstring != vstT):
            myexit("different is verstion between targets.")
        verstring = vstT

    # archive it
    archiveexe = "{}-{}{}".format(configs["name"], verstring, ".exe")
    archiveexefull = os.path.join(configs["archivedir"], archiveexe)
    if not commandargs.skip_archive:
        if isfile(archiveexefull):
            myexit('{} already exists, remove it first.'.format(archiveexefull))

    urlfull = configs['remotedir'] + archiveexe
    if not commandargs.skip_upload:
        if IsRemoteArchiveExists(urlfull):
            myexit('{} already exists'.format(urlfull))

    if not commandargs.skip_archive:
        print("==== creating arhive {} ====".format(archiveexefull))
        args7z = [
            r"C:/LegacyPrograms/7z/7z.exe",
            "a",
            "-sfx7z.sfx",
            archiveexefull,
        ]

        if 'archivingdir' in configs:
            # check the archivingdir only contains outdirs
            archivingfull = os.path.abspath(configs['archivingdir'])
            outdirsfull = []
            for target in configs['targets']:
                outdirsfull.append(os.path.abspath(target['outdir']))
            checkArchivingDir(archivingfull, outdirsfull)

            args7z.append(archivingfull)
        else:
            # no duplicate in args7z
            addedtarget = []
            for t in configs['targets']:
                outdir = t['outdir']
                if outdir not in addedtarget:
                    outdirfull = os.path.abspath(outdir)
                    args7z.append(outdirfull)
                addedtarget.append(outdir)

        args7z.append("-m0=lzma2")
        args7z.append("-mx9")
        args7z.append("-mmt=on")
        args7z.append("-md=512m")
        args7z.append("-mfb=273")
        args7z.append("-ms=on")
     
        print(args7z)
        subprocess.check_call(args7z)

    # upload
    if not commandargs.skip_upload:
        print("==== Uploading to {}... ====".format(configs["remotedir"]))
        daver.dupload(configs["remotedir"], archiveexefull)
        print("Uploaded to {}".format(configs["remotedir"]))

    if not commandargs.skip_hashcheck:
        print("==== Compute sha1 and compare... ====")
        localSha1 = getSha1(archiveexefull)
        remoteSha1Url = configs["remotesha1"].format(archiveexe)

        for loop in range(100):
            try:
                remoteSha1 = urllib.request.urlopen(
                    remoteSha1Url, cafile=certifi.where()).read().decode("utf-8")
                break
            except:
                print(
                    "failed {} times to check remote Sha1. Will try again after waiting 5 seconds.".format(loop+1))
                time.sleep(5)  # wait 5 seconds

        if localSha1.lower() != remoteSha1.lower():
            myexit("sha1 not equal ({} != {}".format(localSha1, remoteSha1))

        print("sha1 check succeed ({})".format(localSha1))

    # update BBS
    if not commandargs.skip_bbs:
        print("==== Updating BBS... ====")
        if not configs["remoteonedrivedir"]:
            myexit("remoteonedrivedir is not specified in config.")

        historyFull = os.path.join(configs['targets'][0]['outdir'],
                                   configs['obtainverfrom'])
        versionReg = configs['obtainverregex']
        updateBBS(configs['name'],
                  verstring,
                  # configs["remotedir"] + archiveexe,
                  configs["remoteonedrivedir"],
                  getChangeLog(historyFull, versionReg)
                  )


def codetest():
    print(updateBBS("testproject", "1.0", "file.zip"))

    remoteSha1 = urllib.request.urlopen("http://ambiesoft.com/ffdav/uploads/getSha1.php?file={}".format(
        "/test/test.txt"), cafile=certifi.where()).read().decode("utf-8")
    print(remoteSha1)


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
    # input('Press ENTER to exit')
