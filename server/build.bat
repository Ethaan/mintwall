@echo off
rem Builds server\avesta74.exe using MSVC Build Tools + vcpkg (C:\vcpkg)
setlocal
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1
cd /d "%~dp0"
if not defined VCPKG_ROOT set VCPKG_ROOT=C:\vcpkg
set "PATH=C:\Program Files\CMake\bin;%VCPKG_ROOT%\downloads\tools\ninja-1.13.2-windows;%PATH%"
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release ^
  -DCMAKE_TOOLCHAIN_FILE=%VCPKG_ROOT%\scripts\buildsystems\vcpkg.cmake ^
  -DVCPKG_TARGET_TRIPLET=x64-windows-static || exit /b 1
cmake --build build || exit /b 1
