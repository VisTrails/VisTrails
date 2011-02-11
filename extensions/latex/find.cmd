@echo off
setlocal enableextensions enabledelayedexpansion

:: Needs an argument.

if "x%*"=="x" (
    echo Usage: which ^<progName^>
    goto :end
)

:: First check if file exists
if exist "%*" (
    echo "%*"
    goto :end
)

:: Then try the unadorned filename in PATH.

set fullspec=
call :find_it %*

:: Then try all adorned filenames in order.

set mypathext=!pathext!
:loop1
    :: Stop if found or out of extensions.

    if "x!mypathext!"=="x" goto :loop1end

    :: Get the next extension and try it.

    for /f "delims=;" %%j in ("!mypathext!") do set myext=%%j
    call :find_it %1!myext!

:: Remove the extension (not overly efficient but it works).

:loop2
    if not "x!myext!"=="x" (
        set myext=!myext:~1!
        set mypathext=!mypathext:~1!
        goto :loop2
    )
    if not "x!mypathext!"=="x" set mypathext=!mypathext:~1!

    goto :loop1
:loop1end

:end
endlocal
goto :eof

:: Function to find and print a file in the path.

:find_it
    for %%i in (%*) do set fullspec=%%~$PATH:i
    set z=%fullspec%
    if not [%fullspec%]==[] set z=%fullspec:\=/%
    if not "x!z!"=="x" @echo !z!
    goto :eof
