import preinstall
import easywebdav
import os
from urllib.parse import urlparse

def dupload(remotedir, archive):
    
    o = urlparse(remotedir)
    
    # Start off by creating a client object. Username and
    # password may be omitted if no authentication is needed.
    webdav = easywebdav.connect(o.hostname, protocol=o.scheme) # protocol='https') # , username='myuser', password='mypass')
    
    updir = o.path
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
    
if __name__ == "__main__":
    dupload('http://example.com/aaa.zip', 'aaa.zip')