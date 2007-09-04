;############################################################################
;##
;## Copyright (C) 2006-2007 University of Utah. All rights reserved.
;##
;## This file is part of VisTrails.
;##
;## This file may be used under the terms of the GNU General Public
;## License version 2.0 as published by the Free Software Foundation
;## and appearing in the file LICENSE.GPL included in the packaging of
;## this file.  Please review the following to ensure GNU General Public
;## Licensing requirements will be met:
;## http://www.opensource.org/licenses/gpl-license.php
;##
;## If you are unsure which license is appropriate for your use (for
;## instance, you are interested in developing a commercial derivative
;## of VisTrails), please contact us at vistrails@sci.utah.edu.
;##
;## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
;## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
;##
;############################################################################
[Setup]
AppName=VisTrails
AppVerName=VisTrails 1.0b (rev896)
WizardImageFile=resources\images\vistrails_icon.bmp
WizardImageStretch=false
WizardImageBackColor=$e3dfe0
DefaultDirName={code:CustomAppDir}\VisTrails
SetupIconFile=resources\icons\vistrails_install2.ico
DefaultGroupName=VisTrails
InfoAfterFile=Input\releaseNotes.txt
DisableDirPage=false
PrivilegesRequired=none
RestartIfNeededByRun=false
ChangesAssociations=true
[Files]
Source: C:\Program Files\ATT\Graphviz\bin\*.dll; DestDir: {app}\vistrails
Source: C:\Program Files\ATT\Graphviz\bin\dot.exe; DestDir: {app}\vistrails
Source: C:\Python25\w9xpopen.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\LICENSE.txt; DestDir: {app}\vistrails\Python25
Source: C:\Python25\pylupdate4.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\pyrcc4.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\python.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\pythonw.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\pyuic4.bat; DestDir: {app}\vistrails\Python25
Source: C:\Python25\README.txt; DestDir: {app}\vistrails\Python25
Source: C:\Python25\sip.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\DLLs\*; DestDir: {app}\vistrails\Python25\DLLs
Source: C:\Python25\include\*; DestDir: {app}\vistrails\Python25\include
Source: C:\Python25\Lib\*; DestDir: {app}\vistrails\Python25\Lib; Flags: recursesubdirs
Source: C:\Python25\libs\*; DestDir: {app}\vistrails\Python25\libs
Source: C:\Python25\Scripts\*; DestDir: {app}\vistrails\Python25\Scripts
Source: C:\Python25\sip\*; DestDir: {app}\vistrails\Python25\sip; Flags: recursesubdirs
Source: C:\Python25\tcl\*; DestDir: {app}\vistrails\Python25\tcl; Flags: recursesubdirs
Source: C:\Python25\Tools\*; DestDir: {app}\vistrails\Python25\Tools; Flags: recursesubdirs
Source: C:\src\VTKbuild\Wrapping\Python\vtk\*; DestDir: {app}\vistrails\vtk; Flags: recursesubdirs
Source: ..\..\examples\*.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\data\torus.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\carotid.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\gktbhFA.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\gktbhL123.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\head.120.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\spx.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\vslice_circ1.bp; DestDir: {app}\examples\data; Components: examples
Source: ..\..\vistrails\*; DestDir: {app}\vistrails; Flags: recursesubdirs
Source: Input\startup.py; DestDir: {%HOMEDRIVE}\{%HOMEPATH}\.vistrails; Flags: onlyifdoesntexist uninsneveruninstall
Source: Input\unzip.exe; DestDir: {app}\vistrails
Source: Input\zip.exe; DestDir: {app}\vistrails
Source: Input\*.dll; DestDir: {app}\vistrails
Source: C:\Qt\4.2.3\bin\*.dll; DestDir: {app}\vistrails
Source: C:\WINDOWS\system32\python25.dll; DestDir: {app}\vistrails
Source: C:\src\VTKbuild\bin\release\*.dll; DestDir: {app}\vistrails
Source: C:\src\VTKbuild\bin\release\*.pyd; DestDir: {app}\vistrails
[Dirs]
Name: {%HOMEDRIVE}\{%HOMEPATH}\.vistrails
Name: {app}\vistrails
Name: {app}\examples; Components: ; Tasks: 
Name: {app}\examples\data
Name: {app}\vistrails\Python25
Name: {app}\vistrails\vtk
Name: {app}\vistrails\vistrails\vtk
Name: {app}\vistrails\vistrails\Python24\DLLs
Name: {app}\vistrails\Python24\include
Name: {app}\vistrails\Python24\Lib
Name: {app}\vistrails\Python24\libs
Name: {app}\vistrails\Python24\Scripts
Name: {app}\vistrails\Python24\sip
Name: {app}\vistrails\Python24\tcl
Name: {app}\vistrails\Python24\Tools
[Components]
Name: main; Description: Main Files; Types: full compact custom; Flags: fixed
Name: examples; Description: Example Files; Types: full

[Icons]
Name: {group}\VisTrails; Filename: {app}\vistrails\Python25\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Components: ; Parameters: vistrails.py -l
Name: {commondesktop}\VisTrails; Filename: {app}\vistrails\Python25\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Parameters: vistrails.py -l
Name: {group}\Uninstall VisTrails; Filename: {uninstallexe}
[Tasks]
Name: desktopicon; Description: Create a &desktop icon; GroupDescription: Additional icons:; Components: main
Name: desktopicon\common; Description: For all users; GroupDescription: Additional icons:; Components: main; Flags: exclusive
Name: desktopicon\user; Description: For the current user only; GroupDescription: Additional icons:; Components: main; Flags: exclusive unchecked
Name: quicklaunchicon; Description: Create a &Quick Launch icon; GroupDescription: Additional icons:; Components: main; Flags: unchecked
Name: associatefiles; Description: Associate *.vt files with VisTrails; GroupDescription: File Association:; Components: main

[Code]
var
	FinishedInstall: Boolean;
function CustomAppDir(Param: String): String;
begin
	if IsAdminLoggedOn then
		Result := ExpandConstant('{pf}')
	else
		Result := ExpandConstant('{userappdata}')
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    FinishedInstall := True;
end;

procedure CurPageChanged(CurPageID: Integer);
var
  oldPythonDir: String;
begin
  case CurPageID of
    wpReady:
    begin
      oldPythonDir := ExpandConstant('{app}') + '\vistrails\Python24';
	  if DirExists(oldPythonDir) then
	    DelTree(oldPythonDir, True, True, True);
	end;
  end;
end;

procedure DeinitializeSetup();
var
  qvtk: String;

  ResultCode: Integer;
begin
  if FinishedInstall then begin
      qvtk := ExpandConstant('{app}') + '\vistrails\packages\spreadsheet\widgets\QVTKWidget';
	  if DirExists(qvtk) then
		DelTree(qvtk, True, True, True);
    end;
end;
[_ISTool]
LogFile=Output\build.log
LogFileAppend=false
[Registry]
Root: HKCR; Subkey: .vt; ValueType: string; ValueData: VisTrailsFile; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKCR; Subkey: VisTrailsFile; ValueType: string; ValueData: VisTrails File; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKCR; Subkey: VisTrailsFile\DefaultIcon; ValueType: string; ValueData: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; Tasks: associatefiles
Root: HKCR; Subkey: VisTrailsFile\shell\open\command; ValueType: string; ValueData: """{app}\vistrails\Python25\python.exe"" ""{app}\vistrails\vistrails.py"" ""%1"""; Tasks: associatefiles
