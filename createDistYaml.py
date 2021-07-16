from posixpath import abspath
import sys
from os.path import isdir, isfile, relpath, join, basename, normpath
from os import walk
from fileinput import filename
import json
import yaml
import collections as cl
import argparse

def buildShouldBeFilesObsoletes(dir):
    results = []
    for (dirpath, _, filenames) in walk(dir):
        for fileName in filenames:
            relDir = relpath(dirpath, dir)
            if relDir == '.':
                relFile = fileName
            else:
                relFile = join(relDir, fileName)
            
            results.append(relFile)
    
    outString="[\n"
    for result in results:
        result = result.replace("\\","\\\\")
        outString += "\t\"" + result + "\"" + ",\n" 

    outString = outString.rstrip()
    outString = outString.rstrip(',')
    
    print(outString+"\n]")

def buildShouldBeFiles(builtDir):
    results = []
    for (dirpath, _, filenames) in walk(builtDir):
        for fileName in filenames:
            relDir = relpath(dirpath, builtDir)
            if relDir == '.':
                relFile = fileName
            else:
                relFile = join(relDir, fileName)
            
            results.append(relFile)
  
    return results

def main():
    '''main'''
    
    parser = argparse.ArgumentParser(description = "Create default yaml used as an input of distSolution")
    parser.add_argument("-sln", type=str, help = "solution file", required=False)
    parser.add_argument("built_directory", 
                        nargs=None, 
                        type=str, 
                        help = "Directory that contains complete files as final distribution")

    #command_arguments is dictinary
    command_arguments = parser.parse_args()

    builtDir = command_arguments.built_directory
    if not isdir(builtDir):
        exit('{0} is not a directory')
        
    defaultName = basename(abspath(normpath(builtDir)))
    if not defaultName:
        defaultName="MyName"

    # keep the yaml output ordered with setting order below
    # results=cl.OrderedDict()
    results = {}
   
    results["name"] = defaultName
    results["solution"] = defaultName +".sln"
    results["targetproject"] = defaultName # "MyProject"
    results["configuration"] = "Release"

    targets=[]
    target = {}
    target["setoutdirforbuild"]=False
    target["outdir"]= builtDir
    target["platform"]="Win32"
    targets.append(target)

    results["targets"] = targets

    results["ShouldBeFiles"] = buildShouldBeFiles(builtDir)
    results["TotalFileCount"] = len(results["ShouldBeFiles"])

    
    results["archivedir"]= "C:\\MyArchive"
    results["remotedir"]= "http://example.com/ffdav/uploads/{}/".format(defaultName)
    results["remotesha1"]= "http://example.com/ffdav/uploads/getSha1.php?file="+ defaultName + "/{}"
    
    results["ShouldNotBeFiles"]= []
    results["ShouldBeOneOfThem"]=[]
    
    results["obtainverfrom"]= "history.txt"
    results["obtainverregex"]= "\\d+\\.\\d+\\.\\d+"

    # jsonStr = json.dumps(results,ensure_ascii=False, indent=4, sort_keys=False, separators=(',', ': '))
    yamlStr = yaml.dump(results, sort_keys=False)
    print(yamlStr)

if __name__ == "__main__":
    main()
    
