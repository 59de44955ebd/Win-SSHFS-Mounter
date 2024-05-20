@echo off
setlocal EnableDelayedExpansion
cd /d %~dp0

:: config
set APP_NAME=Win-SSHFS-Mounter
set APP_ICON=app.ico
set DIR=%CD%
set APP_DIR=%CD%\dist\%APP_NAME%\

:: cleanup
rmdir /s /q "dist\%APP_NAME%" 2>nul
del "dist\%APP_NAME%-x64-setup.exe" 2>nul
del "dist\%APP_NAME%-x64-portable.7z" 2>nul

echo.
echo ****************************************
echo Running pyinstaller...
echo ****************************************

pyinstaller --noupx -w -i "%APP_ICON%" -n "%APP_NAME%" --version-file=version_res.txt -D main.py

echo.
echo ****************************************
echo Copying resources...
echo ****************************************

xcopy /e resources "dist\%APP_NAME%\_internal\resources\" >nul

echo.
echo ****************************************
echo Optimizing dist folder...
echo ****************************************

del "dist\%APP_NAME%\_internal\api-ms-win-core-console-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-datetime-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-debug-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-errorhandling-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l1-2-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-file-l2-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-handle-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-heap-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-interlocked-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-libraryloader-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-localization-l1-2-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-memory-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-namedpipe-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-processenvironment-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-processthreads-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-processthreads-l1-1-1.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-profile-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-rtlsupport-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-string-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-synch-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-synch-l1-2-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-sysinfo-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-timezone-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-core-util-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-conio-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-convert-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-environment-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-filesystem-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-heap-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-locale-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-math-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-process-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-runtime-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-stdio-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-string-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-time-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\api-ms-win-crt-utility-l1-1-0.dll"
del "dist\%APP_NAME%\_internal\libcrypto-3.dll"
del "dist\%APP_NAME%\_internal\ucrtbase.dll"
::del "dist\%APP_NAME%\_internal\_ssl.pyd"
::del "dist\%APP_NAME%\_internal\libssl-3.dll"

if not exist "C:\Program Files (x86)\NSIS\" (
	echo.
	echo ****************************************
	echo NSIS not found at default location, omitting installer creation...
	echo ****************************************
	goto :copy_reg_file
)
echo.
echo ****************************************
echo Creating installer...
echo ****************************************

:: get length of APP_DIR
set TF=%TMP%\x
echo %APP_DIR%> %TF%
for %%? in (%TF%) do set /a LEN=%%~z? - 2
del %TF%

call :make_abs_nsh nsis\uninstall_list.nsh

del "%NSH%" 2>nul

cd "%APP_DIR%"

for /F %%f in ('dir /b /a-d') do (
	echo Delete "$INSTDIR\%%f" >> "%NSH%"
)

for /F %%d in ('dir /s /b /aD') do (
	cd "%%d"
	set DIR_REL=%%d
	for /F %%f IN ('dir /b /a-d 2^>nul') do (
		echo Delete "$INSTDIR\!DIR_REL:~%LEN%!\%%f" >> "%NSH%"
	)
)

cd "%APP_DIR%"

for /F %%d in ('dir /s /b /ad^|sort /r') do (
	set DIR_REL=%%d
	echo RMDir "$INSTDIR\!DIR_REL:~%LEN%!" >> "%NSH%"
)

cd "%DIR%"
set PATH=C:\Program Files (x86)\NSIS;%PATH%
makensis nsis\make-installer.nsi

:copy_reg_file
copy /y "remove-settings.reg" "dist\%APP_NAME%\remove-settings.reg" >nul

if not exist "C:\Program Files\7-Zip\" (
	echo.
	echo ****************************************
	echo 7z.exe not found at default location, omitting .7z creation...
	echo ****************************************
	goto :done
)
echo.
echo ****************************************
echo Creating .7z archive...
echo ****************************************
cd dist
set PATH=C:\Program Files\7-Zip;%PATH%
7z a "%APP_NAME%-x64-portable.7z" "%APP_NAME%\*"
cd ..

:done
echo.
echo ****************************************
echo Done.
echo ****************************************
echo.
pause

endlocal
goto :eof

:make_abs_nsh
set NSH=%~dpnx1%
exit /B