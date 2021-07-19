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
    webdav.mkdir(updir)
    # except ex: #easywebdav.client.OperationFailed as ex:
    #     exit(ex)
    
    remotePath = updir + os.path.basename(archive)
    if webdav.exists(remotePath):
        exit('Already exists on remote:{}'.format(remotePath))
    
    webdav.upload(archive, remotePath)
    
if __name__ == "__main__":
    dupload('http://example.com/aaa.zip', 'aaa.zip')