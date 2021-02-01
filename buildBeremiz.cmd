@echo off
set BEREMIZ_LIB=C:\Users\user26\Beremiz-1.2\python\Lib\user
set HOME_PROJECT=%CD%
cd %BEREMIZ_LIB%
del /Q *.pyc
copy /Y %HOME_PROJECT%\Mespacked.py %BEREMIZ_LIB%\Mespacked.py
copy /Y %HOME_PROJECT%\Algoritm.py %BEREMIZ_LIB%\Algoritm.py
copy /Y %HOME_PROJECT%\NodeInfo.py %BEREMIZ_LIB%\NodeInfo.py
copy /Y %HOME_PROJECT%\NodeObjInfo.py %BEREMIZ_LIB%\NodeObjInfo.py
copy /Y %HOME_PROJECT%\Nodes.py %BEREMIZ_LIB%\Nodes.py
copy /Y %HOME_PROJECT%\PLCGlobals.py %BEREMIZ_LIB%\PLCGlobals.py
copy /Y %HOME_PROJECT%\SocketClient.py %BEREMIZ_LIB%\SocketClient.py
copy /Y %HOME_PROJECT%\switch.py %BEREMIZ_LIB%\switch.py
copy /Y %HOME_PROJECT%\ServerSocketApp.py %BEREMIZ_LIB%\ServerSocketApp.py
copy /Y %HOME_PROJECT%\ServerSocketApp.bat %BEREMIZ_LIB%\ServerSocketApp.bat
@echo on