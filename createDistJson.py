import sys
from os.path import isdir, isfile, relpath, join
from os import walk
from fileinput import filename


def myexit(message):
    print(message)
    exit()

    
def main():
    '''main'''
    if 2 != len(sys.argv):
        myexit('no args')
    
    dir = sys.argv[1]
    if not isdir(dir):
        myexit('{0} is not a directory')
        
    results = []
    for (dirpath, dirnames, filenames) in walk(dir):
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
    
if __name__ == "__main__":
    main()
    
