import daver
from funcs import myexit,showDiffAndExit,getAsFullpath,IsRemoteArchiveExists,getChangeLog
# TEST 

daver.dupload('https://ambiesoft.fam.cx/ffdav/uploads/dicregate/Dicregate-3.6.6.exe', 'C:\\Linkout\\ddd.exe')
IsRemoteArchiveExists('https://ambiesoft.fam.cx/ffdav/uploads/dicregate/Dicregate-3.6.6.exe');