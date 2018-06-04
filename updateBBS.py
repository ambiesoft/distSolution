# -*- coding: utf-8 -*-
import urllib
import time
from _sqlite3 import version
import random

BBSULR='http://ambiesoft.fam.cx/minibbs/minibbs.php'

# https://gist.github.com/masahitojp/863593
def wbs_request(method_string, url, args={}):
    params = urllib.parse.urlencode(args).encode()
    method = method_string.lower()

    if method == ':get':
        resp = urllib.request.urlopen( "%s?%s" % (url, params) )
    elif method == ':post':
        resp = urllib.request.urlopen(url, params)
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

def updateBBS(project, version, archive, info):
    """update bbs"""

    postdata = {
        'act' : 'write',
        'fromscript': 1,
        'name' : 'trueff',
        'email':'ambiesoft.trueff@gmail.com',
        'subject' : '更新されました: {0}'.format(project),
        'delkey' : random.randrange(65535),
        'body' : '{0} ver{1} updated.\n{2}\n\n更新内容：\n{3}'.format(project, version, archive, info)
    }
    
    return wbs_request(":post", BBSULR, postdata)
    