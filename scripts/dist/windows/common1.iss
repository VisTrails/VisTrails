;###############################################################################
;##
;## Copyright (C) 2014-2016, New York University.
;## Copyright (C) 2011-2014, NYU-Poly.
;## Copyright (C) 2006-2011, University of Utah.
;## All rights reserved.
;## Contact: vistrails@sci.utah.edu
;##
;## This file is part of VisTrails.
;##
;## "Redistribution and use in source and binary forms, with or without
;## modification, are permitted provided that the following conditions are met:
;##
;##  - Redistributions of source code must retain the above copyright notice,
;##    this list of conditions and the following disclaimer.
;##  - Redistributions in binary form must reproduce the above copyright
;##    notice, this list of conditions and the following disclaimer in the
;##    documentation and/or other materials provided with the distribution.
;##  - Neither the name of the New York University nor the names of its
;##    contributors may be used to endorse or promote products derived from
;##    this software without specific prior written permission.
;##
;## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
;## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
;## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
;## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
;## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
;## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
;## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
;## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
;## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
;## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
;## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
;##
;###############################################################################

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
  #define python "Python27_64"
  #define python_src "Python27_64_VTK6"
  #define bits "x64"
  #define nbits "64"
  #define sys "Sysnative"
  #define prog "Program Files"
#else
  #define python "Python27"
  #define python_src "Python27_VTK6"
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
Source: C:\{#python_src}\LICENSE.txt; DestDir: {app}\{#python}
Source: C:\{#python_src}\*.exe; DestDir: {app}\{#python}
Source: C:\{#python_src}\README.txt; DestDir: {app}\{#python}
Source: C:\{#python_src}\DLLs\*; DestDir: {app}\{#python}\DLLs
Source: C:\{#python_src}\include\*; DestDir: {app}\{#python}\include
Source: C:\{#python_src}\Lib\*; DestDir: {app}\{#python}\Lib; Flags: recursesubdirs
Source: C:\{#python_src}\libs\*; DestDir: {app}\{#python}\libs
Source: C:\{#python_src}\Scripts\*; DestDir: {app}\{#python}\Scripts
Source: C:\{#python_src}\tcl\*; DestDir: {app}\{#python}\tcl; Flags: recursesubdirs
Source: C:\{#python_src}\Tools\*; DestDir: {app}\{#python}\Tools; Flags: recursesubdirs
Source: {#root}\examples\*; DestDir: {app}\examples; Components: examples; Flags: recursesubdirs
Source: {#root}\scripts\*; Excludes: "dist"; DestDir: {app}\scripts; Flags: recursesubdirs
Source: {#root}\vistrails\*; DestDir: {app}\vistrails; Flags: recursesubdirs
Source: {#root}\extensions\*; DestDir: {app}\extensions; Flags: recursesubdirs
Source: Input\tar.exe; DestDir: {app}
Source: Input\runvistrails.py; DestDir: {app}
Source: Input\*.dll; DestDir: {app}
Source: {#root}\LICENSE; DestDir: {app}; DestName: license.txt
Source: C:\Users\vistrails\vcredist_{#bits}.exe; DestDir: {tmp}; Flags: deleteafterinstall
Source: Input\VisTrails.pdf; DestDir: {app}\doc; Components: usersguide
Source: Input\qt.conf; DestDir: {app}\{#python}

Source: C:\Windows\{#sys}\python27.dll; DestDir: {app}
Source: C:\Windows\{#sys}\python27.dll; DestDir: {app}\{#python}
Source: C:\{#prog}\VTK 6.2.0\bin\*.dll; DestDir: {app}
Source: C:\{#prog}\VTK 6.2.0\bin\*.manifest; DestDir: {app}

;;;; --------    ALPS FILES    ----------;;;;
Source: Input\{#bits}\alps_libs\*; DestDir: {app}; Flags: recursesubdirs

Source: C:\Users\vistrails\src\fftw-3.3.3-dll32\libfftw3-3.dll; DestDir: {app}
Source: C:\Users\vistrails\src\hdf5-1.8.4-32bit-VS2008-IVF101\*; DestDir: {app}\libsrc\hdf5-1.8.4-32bit-VS2008-IVF101; Flags: recursesubdirs
