import daver
from funcs import myexit, showDiffAndExit, getAsFullpath, IsRemoteArchiveExists, getChangeLog
from updateBBS import updateBBS
# TEST 

# daver.dupload('https://ambiesoft.mooo.com/ffdav/uploads/dicregate/Dicregate-3.6.6.exe', 'C:\\Linkout\\ddd.exe')
# IsRemoteArchiveExists('https://ambiesoft.mooo.com/ffdav/uploads/dicregate/Dicregate-3.6.6.exe');

print(updateBBS('aaa',
        'v1.1.1',
        'https://ambiesoft.mooo.com/ffdav/uploads/dicregate/Dicregate-3.6.6.exe',
        'hist'))
