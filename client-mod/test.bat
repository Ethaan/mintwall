@echo off
rem Builds and runs test_walk_pacer.cpp: mintwall.dll's walking logic (walk_pacer.h) against a model of
rem the 7.4 client. Touches nothing the client uses.
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul || exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /O2 /W4 /EHsc test_walk_pacer.cpp /Fobuild\ /Fe:build\test_walk_pacer.exe >build\test_walk_pacer.log || (type build\test_walk_pacer.log & exit /b 1)
build\test_walk_pacer.exe
