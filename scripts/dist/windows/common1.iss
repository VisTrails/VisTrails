WizardImageFile=resources\images\vistrails_icon.bmp
WizardImageStretch=false
WizardImageBackColor=$009D5942
DefaultDirName={code:CustomAppDir}\VisTrails
SetupIconFile=resources\icons\vistrails_install2.ico
InfoAfterFile={#root}\CHANGELOG
PrivilegesRequired=none
RestartIfNeededByRun=false
ChangesAssociations=true
LicenseFile={#root}\LICENSE

; Set 32/64 bit differences
#ifdef bit64
  #define python "Python27_64_VTK6"
  #define bits "x64"
  #define nbits "64"
  #define sys "Sysnative"
  #define prog "Program Files"
#else
  #define python "Python27_VTK6"
  #define bits "x86"
  #define nbits "32"
  #define sys "SysWOW64"
  #define prog "Program Files (x86)"
#endif

#if Exec("C:\" + python + "\python.exe", root + "\scripts\get_usersguide.py Input", ".")
  #error Failed to get usersguide
#endif
#if Exec("C:\" + python + "\python.exe", "update_alps.py alps-vistrails-2.2.b3-win" + nbits + ".zip Input\" + bits + "\alps_libs", ".")
  #error Failed to download ALPS
#endif
#if Exec("C:\" + python + "\python.exe", "..\common\prepare_release.py", ".")
  #error Failed to prepare release
#endif
#if Exec("C:\" + python + "\python.exe", "-m compileall -q " + root + "\vistrails", ".")
  #error Failed to compile source
#endif

[Files]
Source: C:\{#python}\LICENSE.txt; DestDir: {app}\{#python}
Source: C:\{#python}\*.exe; DestDir: {app}\{#python}
Source: C:\{#python}\README.txt; DestDir: {app}\{#python}
Source: C:\{#python}\DLLs\*; DestDir: {app}\{#python}\DLLs
Source: C:\{#python}\include\*; DestDir: {app}\{#python}\include
Source: C:\{#python}\Lib\*; DestDir: {app}\{#python}\Lib; Flags: recursesubdirs
Source: C:\{#python}\libs\*; DestDir: {app}\{#python}\libs
Source: C:\{#python}\Scripts\*; DestDir: {app}\{#python}\Scripts
Source: C:\{#python}\tcl\*; DestDir: {app}\{#python}\tcl; Flags: recursesubdirs
Source: C:\{#python}\Tools\*; DestDir: {app}\{#python}\Tools; Flags: recursesubdirs
Source: {#root}\examples\*; DestDir: {app}\examples; Components: examples; Flags: recursesubdirs
Source: {#root}\scripts\*; Excludes: "dist"; DestDir: {app}\scripts; Flags: recursesubdirs
Source: {#root}\vistrails\*; DestDir: {app}\vistrails; Flags: recursesubdirs
Source: {#root}\extensions\*; DestDir: {app}\extensions; Flags: recursesubdirs
Source: Input\unzip.exe; DestDir: {app}
Source: Input\zip.exe; DestDir: {app}
Source: Input\git.exe; DestDir: {app}
Source: Input\tar.exe; DestDir: {app}
Source: Input\runvistrails.py; DestDir: {app}
Source: Input\*.dll; DestDir: {app}
Source: {#root}\LICENSE; DestDir: {app} DestName: license.txt
Source: C:\Users\vistrails\vcredist_{#bits}.exe; DestDir: {tmp}; Flags: deleteafterinstall
Source: Input\VisTrails.pdf; DestDir: {app}\doc; Components: usersguide
Source: Input\qt.conf; DestDir: {app}\{#python}

Source: C:\Windows\{#sys}\python27.dll; DestDir: {app}
Source: C:\Windows\{#sys}\python27.dll; DestDir: {app}\{#python}
Source: C:\{#prog}\VTK 6.2.0\bin\*.dll; DestDir: {app}

;;;; --------    ALPS FILES    ----------;;;;
Source: Input\{#bits}\alps_libs\*; DestDir: {app}; Flags: recursesubdirs

Source: C:\Users\vistrails\src\fftw-3.3.3-dll32\libfftw3-3.dll; DestDir: {app}
Source: C:\Users\vistrails\src\hdf5-1.8.4-32bit-VS2008-IVF101\*; DestDir: {app}\libsrc\hdf5-1.8.4-32bit-VS2008-IVF101; Flags: recursesubdirs
