@echo off
rem Creates a fresh server\db.db3 from sql\schema.sqlite + sql\seed.sql
setlocal
cd /d "%~dp0"
set SQLITE=build\vcpkg_installed\x64-windows-static\tools\sqlite3.exe
if not exist "%SQLITE%" set SQLITE=build\vcpkg_installed\x64-windows-static\tools\sqlite3\sqlite3.exe
if exist db.db3 ( echo db.db3 already exists - delete it first to recreate & exit /b 1 )
"%SQLITE%" db.db3 < sql\schema.sqlite || exit /b 1
"%SQLITE%" db.db3 < sql\seed.sql || exit /b 1
echo Created db.db3
