;############################################################################
;##
;## Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
AppVerName=VisTrails 1.6 beta
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
Source: C:\Python26\w9xpopen.exe; DestDir: {app}\vistrails\Python26
Source: C:\Python26\*.dll; DestDir: {app}\vistrails\Python26
Source: C:\Python26\LICENSE.txt; DestDir: {app}\vistrails\Python26
Source: C:\Python26\python.exe; DestDir: {app}\vistrails\Python26
Source: C:\Python26\pythonw.exe; DestDir: {app}\vistrails\Python26
Source: C:\Python26\README.txt; DestDir: {app}\vistrails\Python26
Source: C:\Python26\DLLs\*; DestDir: {app}\vistrails\Python26\DLLs
Source: C:\Python26\include\*; DestDir: {app}\vistrails\Python26\include
Source: C:\Python26\Lib\*; DestDir: {app}\vistrails\Python26\Lib; Flags: recursesubdirs
Source: C:\Python26\libs\*; DestDir: {app}\vistrails\Python26\libs
Source: C:\Python26\Scripts\*; DestDir: {app}\vistrails\Python26\Scripts
Source: C:\Python26\tcl\*; DestDir: {app}\vistrails\Python26\tcl; Flags: recursesubdirs
Source: C:\Python26\Tools\*; DestDir: {app}\vistrails\Python26\Tools; Flags: recursesubdirs
Source: ..\..\examples\brain_vistrail.vt; DestDir: {app}\examples; Components: examples
Source: ..\..\examples\chebi_webservice.vt; DestDir: {app}\examples; Components: examples
;Source: ..\..\examples\cmop_starter_trail.vt; DestDir: {app}\examples; Components: examples
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
Source: ..\..\examples\r_stats.vt; DestDir: {app}\examples; Components: examples
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
Source: ..\..\extensions\*; DestDir: {app}\extensions; Flags: recursesubdirs
Source: Input\unzip.exe; DestDir: {app}\vistrails
Source: Input\zip.exe; DestDir: {app}\vistrails
Source: Input\git.exe; DestDir: {app}\vistrails
Source: Input\tar.exe; DestDir: {app}\vistrails
Source: Input\runvistrails.py; DestDir: {app}
Source: Input\*.dll; DestDir: {app}\vistrails
Source: Input\license.txt; DestDir: {app}
Source: Input\vcredist_x86.exe; DestDir: {tmp}; Flags: deleteafterinstall
;;;; ------- QT LIBS ------- ;;;;
;Source: D:\Qt\4.6.2\bin\*.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\phonon4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\Qt3Support4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtAssistantClient4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtCLucene4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtCore4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtDesigner4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtDesignerComponents4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtGui4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtHelp4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtMultimedia4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtNetwork4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtOpenGL4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtScript4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtScriptTools4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtSql4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtSvg4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtTest4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtWebKit4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtXml4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\bin\QtXmlPatterns4.dll; DestDir: {app}\vistrails
Source: D:\Qt\4.6.2\plugins\iconengines\*; DestDir: {app}\vistrails\Python26\plugins\iconengines
Source: D:\Qt\4.6.2\plugins\imageformats\*; DestDir: {app}\vistrails\Python26\plugins\imageformats
Source: Input\qt.conf; DestDir: {app}\vistrails\Python26
;Source: C:\WINDOWS\system32\Python26.dll; DestDir: {app}\vistrails
;Source: C:\WINDOWS\system32\Python26.dll; DestDir: {app}\vistrails\Python26
Source: D:\src\vtk-5.6\bin32\bin\Release\*.dll; DestDir: {app}\vistrails
;Source: E:\src\VTKbuild\bin\release\*.pyd; DestDir: {app}\vistrails
;Source: D:\src\VTKbuild\Wrapping\Python\vtk\*; DestDir: {app}\vistrails\vtk; Flags: recursesubdirs
Source: D:\emanuele\src\netcdf-3.6.1\src\lib\*.dll; DestDir: {app}\vistrails
;;;; --------    ALPS FILES    ----------;;;;
Source: Input\alps_libs\vistrails\*; DestDir: {app}\vistrails; Flags: recursesubdirs
;;;; --------    ITK FILES    ----------;;;;
;Source: E:\src\itk\Wrapping\WrapITK\Python\Release\*; DestDir: {app}\vistrails; Flags: recursesubdirs
;Source: E:\src\itk\Wrapping\WrapITK\Python\Release\itkExtras\*; DestDir: {app}\itkExtras; Flags: recursesubdirs
;Source: E:\src\itk\Wrapping\WrapITK\Python\Release\Configuration\*; DestDir: {app}\Configuration; Flags: recursesubdirs
;Source: E:\src\itk\bin\Release\*.dll; DestDir: {app}\vistrails
;Source: E:\src\itk\bin\Release\*.pyd; DestDir: {app}\vistrails
;Source: E:\src\itk\bin\Release\*.py; DestDir: {app}\vistrails
;;;; --------- END OF ITK FILES --------- ;;;;
Source: D:\src\fftw-3.2.2.pl1-dll32\libfftw3-3.dll; DestDir: {app}\vistrails
Source: D:\emanuele\src\hdf5-1.8.4-32bit-VS2008-IVF101\*; DestDir: {app}\vistrails\libsrc\hdf5-1.8.4-32bit-VS2008-IVF101; Flags: recursesubdirs

[Dirs]
Name: {%HOMEDRIVE}\{%HOMEPATH}\.vistrails
Name: {app}\vistrails
;;Name: {app}\Configuration
;;Name: {app}\itkExtras
Name: {app}\examples; Components: examples; Tasks: 
Name: {app}\examples\vtk_examples
Name: {app}\examples\data
Name: {app}\extensions; Components: extensions; Tasks: 
Name: {app}\scripts
Name: {app}\scripts\gen_vtk_examples
Name: {app}\vistrails\libsrc
Name: {app}\vistrails\Python26
Name: {app}\vistrails\vtk
Name: {app}\vistrails\vistrails\vtk
Name: {app}\vistrails\vistrails\Python24\DLLs
Name: {app}\vistrails\Python26\include
Name: {app}\vistrails\Python26\Lib
Name: {app}\vistrails\Python26\libs
Name: {app}\vistrails\Python26\Scripts
Name: {app}\vistrails\Python26\sip
Name: {app}\vistrails\Python26\tcl
Name: {app}\vistrails\Python26\Tools
[Components]
Name: main; Description: Main Files; Types: full compact custom; Flags: fixed
Name: examples; Description: Example Files; Types: full
Name: extensions; Description: Extension Files; Types: full

[Icons]
Name: {group}\VisTrails; Filename: {app}\vistrails\Python26\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Components: ; Parameters: vistrails.py
Name: {commondesktop}\VisTrails; Filename: {app}\vistrails\Python26\python.exe; WorkingDir: {app}\vistrails; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Parameters: vistrails.py; Components: main; Tasks: desktopicon
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
Root: HKCR; Subkey: VisTrailsFile\shell\open\command; ValueType: string; ValueData: """{app}\vistrails\Python26\python.exe"" ""{app}\runvistrails.py"" ""{app}\vistrails\Python26\python.exe"" ""{app}\vistrails\vistrails.py"" ""{app}\vistrails"" ""%1"""; Tasks: associatefiles; Flags: uninsdeletekey
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
Name: {app}\vistrails\Python25; Type: filesandordirs
Name: {app}\vistrails\vtk; Type: filesandordirs
Name: {app}\vistrails\*.pyd; Type: files
Name: {app}\vistrails\dgnlib.dll; Type: files
Name: {app}\vistrails\_Xdmf.dll; Type: files
Name: {app}\vistrails\geotiff.dll; Type: files
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

procedure DeleteVCRedistRuntimeTemporaryFiles();
var
   i : Integer;
   byCounter : Byte;
   byDrive : Byte;
   strFile1, strFile2, strFile3 : String;
   strRootDrivePath : String;
   //totally there are 24 files to be deleted
   arrFiles : Array [1..24] Of String;
begin

   //We will check the following root drives
   //C, D, E, F, G, H, I, J, K, L, M
   For byCounter := 67 to 77 do
   Begin
      strRootDrivePath := Chr(byCounter) + ':\';
      arrFiles[1] := strRootDrivePath + 'vcredist.bmp';
      arrFiles[2] := strRootDrivePath + 'VC_RED.cab';
      arrFiles[3] := strRootDrivePath + 'VC_RED.MSI';

      //If these 3 files then we have found the right
      //drive in which the VC runtime files are extracted
      If (FileExists(arrFiles[1]) And
          FileExists(arrFiles[2]) And
          FileExists(arrFiles[3])) Then
      Begin

          arrFiles[4] := strRootDrivePath + 'eula.1028.txt';
          arrFiles[5] := strRootDrivePath + 'eula.1031.txt';
          arrFiles[6] := strRootDrivePath + 'eula.1033.txt';
          arrFiles[7] := strRootDrivePath + 'eula.1036.txt';
          arrFiles[8] := strRootDrivePath + 'eula.1040.txt';
          arrFiles[9] := strRootDrivePath + 'eula.1041.txt';
          arrFiles[10] := strRootDrivePath + 'eula.1042.txt';
          arrFiles[11] := strRootDrivePath + 'eula.2052.txt';
          arrFiles[12] := strRootDrivePath + 'eula.3082.txt';
          arrFiles[13] := strRootDrivePath + 'globdata.ini';
          arrFiles[14] := strRootDrivePath + 'install.exe';
          arrFiles[15] := strRootDrivePath + 'install.ini';
          arrFiles[16] := strRootDrivePath + 'install.res.1028.dll';
          arrFiles[17] := strRootDrivePath + 'install.res.1031.dll';
          arrFiles[18] := strRootDrivePath + 'install.res.1033.dll';
          arrFiles[19] := strRootDrivePath + 'install.res.1036.dll';
          arrFiles[20] := strRootDrivePath + 'install.res.1040.dll';
          arrFiles[21] := strRootDrivePath + 'install.res.1041.dll';
          arrFiles[22] := strRootDrivePath + 'install.res.1042.dll';
          arrFiles[23] := strRootDrivePath + 'install.res.2052.dll';
          arrFiles[24] := strRootDrivePath + 'install.res.3082.dll';

          For i := 1 to 24 Do
          Begin
            DeleteFile(arrFiles[i]);
          End;

          //Now that we have found and deleted all the files
          //we will break
          Break;
      End;
   End;
End;

procedure DeinitializeSetup();
var
  qvtk: String;
begin
  if FinishedInstall then begin
      qvtk := ExpandConstant('{app}') + '\vistrails\packages\spreadsheet\widgets\QVTKWidget';
	  if DirExists(qvtk) then
		DelTree(qvtk, True, True, True);
  end;
  DeleteVCRedistRuntimeTemporaryFiles();
end;
