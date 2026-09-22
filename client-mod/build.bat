@echo off
rem Builds client-mod\build\mintwall.dll (32-bit, like the 7.4 client) with MSVC Build Tools.
rem tools\patch-client.ps1 copies it next to Tibia-mintwall.exe.
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars32.bat" >nul || exit /b 1
cd /d "%~dp0"
if not exist build mkdir build
cl /nologo /O2 /MT /W4 /EHsc /LD mintwall.cpp /Fobuild\ /Fe:build\mintwall.dll /link user32.lib || exit /b 1
