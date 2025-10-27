# -*- coding: utf-8 -*-
import urllib
import time
# from _sqlite3 import version
import random
import certifi

# BBSULR='https://ambiesoft.com/minibbs/minibbs.php'
BBSULR = 'https://script.google.com/macros/s/AKfycbwjWk-b48HhljeR33bwfZHPOpNXbGPkWc5PQ8Meb_lg4g3w9NILL96MPf3DgLnjgXen3A/exec';

# https://gist.github.com/masahitojp/863593
def wbs_request(method_string, url, args={}):
    params = urllib.parse.urlencode(args).encode()
    method = method_string.lower()

    if method == ':get':
        resp = urllib.request.urlopen( "%s?%s" % (url, params), cafile=certifi.where() )
    elif method == ':post':
        resp = urllib.request.urlopen(url,params, cafile=certifi.where())
    elif method in ['put', 'delete']:
        raise Exception('Not yet supported')
    else:
        raise Exception('Unsupported http method')

    return resp.read()

import datetime
import requests
def wbs_requestGBBS(postdata):
    GAS_URL = "https://script.google.com/macros/s/AKfycbwjWk-b48HhljeR33bwfZHPOpNXbGPkWc5PQ8Meb_lg4g3w9NILL96MPf3DgLnjgXen3A/exec"

    SendDATA = {
        "name": postdata['name'],
        "message": postdata['body'],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    response = requests.post(
        GAS_URL,
        headers={"Content-Type": "application/json"},
        json=SendDATA
    )

    print("Update GBBS Status:", response.status_code)
    print("Update GBBS Response:", response.text)

if __name__ == '__main__':
    pass

def updateBBS(project, version, archive, info):
    """update bbs"""

    postdata = {
        'act' : 'write',
        'fromscript': 1,
        'name' : 'trueff',
        'email':'ambiesoft.trueff@gmail.com',
        'subject' : '更新されました: {0}'.format(project),
        'delkey' : random.randrange(65535),
        # 'body' : '{0} ver{1} updated.\n{2}\n\n更新内容：\n{3}'.format(project, version, archive, info)
        'body' : '{0} is updated to ver{1}.\n{2}\n\n更新内容：\n{3}'.format(project, version, archive, info).strip()
    }
    
    # return wbs_request(":get", BBSULR, postdata)
    return wbs_requestGBBS(postdata)
    
