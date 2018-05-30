# -*- coding: utf-8 -*-
import urllib
import time
from _sqlite3 import version

BBSULR='http://ambiesoft.fam.cx/minibbs/minibbs.php'

# https://gist.github.com/masahitojp/863593
def wbs_request(method_string, url, args={}):
    params = urllib.urlencode(args)
    method = method_string.lower()

    if method == ':get':
        resp = urllib.urlopen( "%s?%s" % (url, params) )
    elif method == ':post':
        resp = urllib.urlopen(url, params)
    elif method in ['put', 'delete']:
        raise Exception('Not yet supported')
    else:
        raise Exception('Unsupported http method')

    return resp.read()

if __name__ == '__main__':
    print( wbs_request(":get",'http://blog.udzura.jp/', {'s': 'Ruby'}))

    postdata = {
        '__mk_ja_JP' : 'カタカナ',
        'initialSearch' : 1,
        'url' : 'search-alias',
        'field-keywords': 'python',
        'Go' : 'Go'
    }
    print( wbs_request(":POST", 'http://www.amazon.co.jp/s/', postdata))

def updateBBS(project, version, archive):
    """update bbs"""

    postdata = {
        'act' : 'write',
        'name' : 'trueff',
        'email':'ambiesoft.trueff@gmail.com',
        'subject' : 'Updated {0}'.format(project),
        'delkey' : 'aaaa',
        'body' : '{0} ver{1} updated.'.format(project, version)
    }
    
    return wbs_request(":post", BBSULR, postdata)
    