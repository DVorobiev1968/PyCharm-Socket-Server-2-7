@echo off
chcp 1251 > nul
set BEREMIZ_LIB=C:\Users\user26\Beremiz-1.2\python\Lib\
set BEREMIZ_LIB_SERVER=%BEREMIZ_LIB%\Server
set BEREMIZ_LIB_CLIENT=%BEREMIZ_LIB%\Client
set HOME_PROJECT=%CD%
set SERVER_DIR=%HOME_PROJECT%\Server
set CLIENT_DIR=%HOME_PROJECT%\Client
mkdir %BEREMIZ_LIB_SERVER%
mkdir %BEREMIZ_LIB_CLIENT%
del /Q %BEREMIZ_LIB_SERVER%\*.pyc
del /Q %BEREMIZ_LIB_CLIENT%\*.pyc

copy /Y %SERVER_DIR%\Mespacked.py %BEREMIZ_LIB_SERVER%\Mespacked.py
copy /Y %SERVER_DIR%\AlgoritmInfo.py %BEREMIZ_LIB_SERVER%\AlgoritmInfo.py
copy /Y %SERVER_DIR%\NodeInfo.py %BEREMIZ_LIB_SERVER%\NodeInfo.py
copy /Y %SERVER_DIR%\NodeObjInfo.py %BEREMIZ_LIB_SERVER%\NodeObjInfo.py
copy /Y %SERVER_DIR%\Nodes.py %BEREMIZ_LIB_SERVER%\Nodes.py
copy /Y %SERVER_DIR%\PLCGlobals.py %BEREMIZ_LIB_SERVER%\PLCGlobals.py
copy /Y %SERVER_DIR%\switch.py %BEREMIZ_LIB_SERVER%\switch.py
copy /Y %SERVER_DIR%\ServerSocketApp.py %BEREMIZ_LIB_SERVER%\ServerSocketApp.py
copy /Y %SERVER_DIR%\__init__.py %BEREMIZ_LIB_SERVER%\__init__.py

copy /Y %CLIENT_DIR%\SocketClient.py %BEREMIZ_LIB_CLIENT%\SocketClient.py
copy /Y %CLIENT_DIR%\__init__.py %BEREMIZ_LIB_CLIENT%\__init__.py

copy /Y %HOME_PROJECT%\ServerSocketApp.bat %BEREMIZ_LIB%ServerSocketApp.bat

@echo on