import os
import re
import urllib
import urllib.request

def getAsFullpath(files, outdir):
    return [os.path.realpath(os.path.join(outdir, item)) for item in files]

def getFileCount(d):
    total = 0
    for _, _, files in os.walk(d):
        total += len(files)
    return total

# https://stackoverflow.com/a/6486513
def getPathDiffs(first, second):
    first = set(first)
    second = set(second)
    return ([item for item in  second if item not in first],[item for item in first if item not in second])

def getFileListAsFullPath(outdir):
    f = []
    for (dirpath, dirnames, filenames) in os.walk(outdir):
      for name in filenames:
        f.append(os.path.realpath( os.path.join(dirpath, name)))

    # return [f for f in os.listdir(outdir) if os.path.isfile(os.path.join(outdir, f))]
    return f


def myexit(message, retval=1):
    
    print('DistError: ' + message)
    # input('Press ENTER to exit')
    exit(retval)
    
    
def showDiffAndExit(outdir, shouldBeFull, shouldTotal, exact):
    
    current = getFileListAsFullPath(outdir)
    (targetOver, listOver) = getPathDiffs(shouldBeFull,current);
    
    message = ''
    if(targetOver):
        message += "Target directory contains following unlisted files:\n"
        message += "\n".join(str(e) for e in targetOver)
    if(listOver):
        message == "\n"
        message += "[ShouldBeFiles] list contains following non-existent files:\n"
        message += "\n".join(str(e) for e in listOver)
    
    if(exact):
        if(message):
            myexit(message)
    else:
        message = "TotalFileCount different. ({} != {})\n".format(shouldTotal, getFileCount(outdir)) + message
        myexit(message)    
        
        
def IsRemoteArchiveExists(url):
    print(url)
    request = urllib.request.Request(url);
    request.get_method = lambda : 'HEAD'
    
    status = 0
    try:
        responce = urllib.request.urlopen(request)
        status = responce.status
    except urllib.error.HTTPError as e:
        status = e.code
        
    if status==200:
        return True
    elif status==404:
        # OK 
        return False
    else:
        myexit("HEAD request returns invalid status {0}.".format(responce.status))

def getChangeLog(fileName, regstr):
    rets = []
    getFirst = False
    with open(fileName, "r", encoding="utf-8") as f:
        for line in f.readlines():
            m = re.search(regstr, line)
        
            if m and m.group(0):
                if not getFirst:
                    getFirst=True
                    continue
                return ''.join(rets)
            rets.append(line)
    return ''.join(rets)            

