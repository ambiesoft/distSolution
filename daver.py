import easywebdav
import os

def dupload(archive):
    # Start off by creating a client object. Username and
    # password may be omitted if no authentication is needed.
    webdav = easywebdav.connect('ambiesoft.fam.cx') # , username='myuser', password='mypass')
    
    updir = '/ffdav/uploads/dicregate/'
    try:
        webdav.mkdir(updir)
    except easywebdav.client.OperationFailed:
        pass
    
    #webdav.rmdir('another_dir')
    # webdav.download('remote/path/to/file', 'local/target/file')
    

    remotePath = updir + os.path.basename(archive)
    if webdav.exists(remotePath):
        print('Already exists on remote:{}'.format(remotePath))
        exit(1)
    
    webdav.upload(archive, remotePath)
    
