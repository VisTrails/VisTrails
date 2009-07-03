;############################################################################
;##
;## Copyright (C) 2006-2009 University of Utah. All rights reserved.
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
AppVerName=VisTrails 1.3
WizardImageFile=resources\images\vistrails_icon.bmp
WizardImageStretch=false
WizardImageBackColor=$9d5942
DefaultDirName={code:CustomAppDir}\VisTrails
SetupIconFile=resources\icons\vistrails_install2.ico
DefaultGroupName=VisTrails
InfoAfterFile=Input\releaseNotes.txt
DisableDirPage=false
PrivilegesRequired=none
RestartIfNeededByRun=false
ChangesAssociations=true
LicenseFile=Input\license.txt
[Files]
Source: C:\Python25\w9xpopen.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\*.dll; DestDir: {app}\vistrails\Python25
Source: C:\Python25\LICENSE.txt; DestDir: {app}\vistrails\Python25
Source: C:\Python25\python.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\python.exe.manifest; DestDir: {app}\vistrails\Python25
Source: C:\Python25\pythonw.exe; DestDir: {app}\vistrails\Python25
Source: C:\Python25\README.txt; DestDir: {app}\vistrails\Python25
Source: C:\Python25\DLLs\*; DestDir: {app}\vistrails\Python25\DLLs
Source: C:\Python25\include\*; DestDir: {app}\vistrails\Python25\include
Source: C:\Python25\Lib\*; DestDir: {app}\vistrails\Python25\Lib; Flags: recursesubdirs
Source: C:\Python25\libs\*; DestDir: {app}\vistrails\Python25\libs
Source: C:\Python25\Scripts\*; DestDir: {app}\vistrails\Python25\Scripts
Source: C:\Python25\tcl\*; DestDir: {app}\vistrails\Python25\tcl; Flags: recursesubdirs
Source: C:\Python25\Tools\*; DestDir: {app}\vistrails\Python25\Tools; Flags: recursesubdirs
Source: E:\src\VTKbuild\Wrapping\Python\vtk\*; DestDir: {app}\vistrails\vtk; Flags: recursesubdirs
Source: ..\..\examples\brain_vistrail.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\chebi_webservice.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\cmop_starter_trail.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\DataTransformation_webservice.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\DDBJ_webservice.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\EMBOSS_webservices.vt; DestDir: {app}\examples; Components: examples
;Source: ..\..\examples\gridfieldexample.vt; DestDir: {app}\examples; Components: examples
;Source: ..\..\examples\bathymetry.vt; DestDir: {app}\examples; Components: examples
;Source: ..\..\examples\croos2.vt; DestDir: {app}\examples; Components: examples
;Source: ..\..\examples\gridfieldexample.xml; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\head.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\KEGG_SearchEntities_webservice.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\KEGG_webservices.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\lung.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\noaa_webservices.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\offscreen.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\plot.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\protein_visualization.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\spx.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\structure_or_id_webservice.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\terminator.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\triangle_area.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\vtk.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\vtk_book_3rd_p189.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\vtk_book_3rd_p193.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\vtk_examples\*; DestDir: {app}\examples\vtk_examples; Components: examples; Flags: recursesubdirs
Source: ..\..\examples\vtk_http.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\XSLTSample.xsl; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\data\torus.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\carotid.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\gktbhFA.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\gktbhL123.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\head.120.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\spx.vtk; DestDir: {app}\examples\data; Components: examples
Source: ..\..\examples\data\vslice_circ1.bp; DestDir: {app}\examples\data; Components: examples
Source: ..\..\scripts\*; DestDir: {app}\scripts; Flags: recursesubdirs
Source: ..\..\vistrails\*; DestDir: {app}\vistrails; Flags: recursesubdirs
Source: Input\unzip.exe; DestDir: {app}\vistrails
Source: Input\zip.exe; DestDir: {app}\vistrails
Source: Input\runvistrails.py; DestDir: {app}
Source: Input\*.dll; DestDir: {app}\vistrails
Source: Input\license.txt; DestDir: {app}
Source: Input\vcredist_x86.exe; DestDir: {tmp}; Flags: deleteafterinstall
;Source: C:\Qt\4.4.0\bin\*.dll; DestDir: {app}\vistrails
Source: C:\Python25\Lib\site-packages\PyQt4\plugins\iconengines\*; DestDir: {app}\vistrails\Python25\plugins\iconengines
Source: C:\Python25\Lib\site-packages\PyQt4\plugins\imageformats\*; DestDir: {app}\vistrails\Python25\plugins\imageformats
Source: Input\qt.conf; DestDir: {app}\vistrails\Python25
;Source: C:\WINDOWS\system32\python25.dll; DestDir: {app}\vistrails
;Source: C:\WINDOWS\system32\python25.dll; DestDir: {app}\vistrails\Python25
Source: E:\src\VTKbuild\bin\release\*.dll; DestDir: {app}\vistrails
Source: E:\src\VTKbuild\bin\release\*.pyd; DestDir: {app}\vistrails
Source: E:\emanuele\src\netcdf-3.6.1\src\lib\*.dll; DestDir: {app}\vistrails
[Dirs]
Name: {%HOMEDRIVE}\{%HOMEPATH}\.vistrails
Name: {app}\vistrails
Name: {app}\examples; Components: examples; Tasks: 
Name: {app}\examples\vtk_examples
Name: {app}\examples\data
Name: {app}\scripts
Name: {app}\scripts\gen_vtk_examples
Name: {app}\vistrails\Python25
Name: {app}\vistrails\vtk
Name: {app}\vistrails\vistrails\vtk
Name: {app}\vistrails\vistrails\Python24\DLLs
Name: {app}\vistrails\Python25\include
Name: {app}\vistrails\Python25\Lib
Name: {app}\vistrails\Python25\libs
Name: {app}\vistrails\Python25\Scripts
Name: {app}\vistrails\Python25\sip
Name: {app}\vistrails\Python25\tcl
Name: {app}\vistrails\Python25\Tools
[Components]
Name: main; Description: Main Files; Types: full compact custom; Flags: fixed
Name: examples; Description: Example Files; Types: full

[Icons]
Name: {group}\VisTrails; Filename: {app}\vistrails\Python25\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Components: ; Parameters: vistrails.py
Name: {commondesktop}\VisTrails; Filename: {app}\vistrails\Python25\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Parameters: vistrails.py; Components: main; Tasks: desktopicon
Name: {group}\Uninstall VisTrails; Filename: {uninstallexe}
[Tasks]
Name: desktopicon; Description: Create a &desktop icon; GroupDescription: Additional icons:; Components: main
Name: desktopicon\common; Description: For all users; GroupDescription: Additional icons:; Components: main; Flags: exclusive
Name: desktopicon\user; Description: For the current user only; GroupDescription: Additional icons:; Components: main; Flags: exclusive unchecked
Name: quicklaunchicon; Description: Create a &Quick Launch icon; GroupDescription: Additional icons:; Components: main; Flags: unchecked
Name: associatefiles; Description: Associate *.vt files with VisTrails; GroupDescription: File Association:; Components: main
[_ISTool]
LogFile=Output\build.log
LogFileAppend=false
[Registry]
Root: HKCR; Subkey: .vt; ValueType: string; ValueData: VisTrailsFile; Flags: uninsdeletevalue; Tasks: associatefiles
Root: HKCR; Subkey: VisTrailsFile; ValueType: string; ValueData: VisTrails File; Flags: uninsdeletekey; Tasks: associatefiles
Root: HKCR; Subkey: VisTrailsFile\DefaultIcon; ValueType: string; ValueData: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; Tasks: associatefiles; Flags: uninsdeletekey
Root: HKCR; Subkey: VisTrailsFile\shell\open\command; ValueType: string; ValueData: """{app}\vistrails\Python25\python.exe"" ""{app}\runvistrails.py"" ""{app}\vistrails\Python25\python.exe"" ""{app}\vistrails\vistrails.py"" ""{app}\vistrails"" ""%1"""; Tasks: associatefiles; Flags: uninsdeletekey
Root: HKCR; Subkey: .vtl; ValueType: string; ValueData: VisTrailsFile; Flags: uninsdeletevalue; Tasks: associatefiles
[InstallDelete]
Name: {app}\vistrails\dot.exe; Type: files
Name: {app}\vistrails\freetype6.dll; Type: files
Name: {app}\vistrails\jpeg.dll; Type: files
Name: {app}\vistrails\libexpat.dll; Type: files
Name: {app}\vistrails\libexpatw.dll; Type: files
Name: {app}\vistrails\png.dll; Type: files
Name: {app}\vistrails\z.dll; Type: files
Name: {app}\vistrails\zlib1.dll; Type: files
Name: {app}\vistrails\python24.dll; Type: files
Name: {app}\vistrails\Python24; Type: filesandordirs
Name: {app}\examples\gridfieldexample.vt; Type: files
Name: {app}\vistrails\vistrails; Type: filesandordirs
Name: {app}\vistrails\packages\gridfield; Type: filesandordirs
[Run]
Filename: {tmp}\vcredist_x86.exe; Parameters: /Q; Components: ; Tasks: 


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
begin
//  case CurPageID of
//    wpReady:
//    begin
//	  DeleteFile(ExpandConstant('{app}') + '\vistrails\python24.dll');
//      oldPythonDir := ExpandConstant('{app}') + '\vistrails\Python24';
//	  if DirExists(oldPythonDir) then
//	    DelTree(oldPythonDir, True, True, True);}
//	end;
//  end;
end;

procedure DeinitializeSetup();
var
  qvtk: String;
begin
  if FinishedInstall then begin
      qvtk := ExpandConstant('{app}') + '\vistrails\packages\spreadsheet\widgets\QVTKWidget';
	  if DirExists(qvtk) then
		DelTree(qvtk, True, True, True);
    end;
end;
