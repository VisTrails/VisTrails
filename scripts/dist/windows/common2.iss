[Dirs]
Name: {app}\vistrails
Name: {app}\examples; Components: examples; Tasks: 
Name: {app}\extensions; Components: extensions; Tasks:
Name: {app}\doc; Components: usersguide; Tasks:  
Name: {app}\scripts
Name: {app}\scripts\gen_vtk_examples
Name: {app}\libsrc
Name: {app}\{#python}
Name: {app}\{#python}\DLLs
Name: {app}\{#python}\include
Name: {app}\{#python}\Lib
Name: {app}\{#python}\libs
Name: {app}\{#python}\Scripts
Name: {app}\{#python}\sip
Name: {app}\{#python}\tcl
Name: {app}\{#python}\Tools
[Components]
Name: main; Description: Main Files; Types: full compact custom; Flags: fixed
Name: examples; Description: Example Files; Types: full
Name: extensions; Description: Extension Files; Types: full
Name: usersguide; Description: User's Guide PDF document; Types: full

[Icons]
Name: {group}\VisTrails; Filename: {app}\{#python}\python.exe; WorkingDir: {app}; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Components: ; Parameters: vistrails\run.py
Name: {commondesktop}\VisTrails; Filename: {app}\{#python}\python.exe; WorkingDir: {app}; IconFilename: {app}\vistrails\gui\resources\images\vistrails_icon_small.ico; IconIndex: 0; Parameters: vistrails\run.py; Components: main; Tasks: desktopicon
Name: {group}\Uninstall VisTrails; Filename: {uninstallexe}
Name: {group}\VisTrails.pdf; Filename: {app}\doc\VisTrails.pdf; Components: usersguide
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
Root: HKCR; Subkey: VisTrailsFile\shell\open\command; ValueType: string; ValueData: """{app}\{#python}\python.exe"" ""{app}\runvistrails.py"" ""{app}\{#python}\python.exe"" ""{app}\vistrails\run.py"" ""{app}"" ""%1"""; Tasks: associatefiles; Flags: uninsdeletekey
Root: HKCR; Subkey: .vtl; ValueType: string; ValueData: VisTrailsFile; Flags: uninsdeletevalue; Tasks: associatefiles
[InstallDelete]
Name: {app}\dot.exe; Type: files
Name: {app}\freetype6.dll; Type: files
Name: {app}\jpeg.dll; Type: files
Name: {app}\libexpat.dll; Type: files
Name: {app}\libexpatw.dll; Type: files
Name: {app}\png.dll; Type: files
Name: {app}\z.dll; Type: files
Name: {app}\zlib1.dll; Type: files
Name: {app}\{#python}; Type: filesandordirs
Name: {app}\*.pyd; Type: files
Name: {app}\dgnlib.dll; Type: files
Name: {app}\_Xdmf.dll; Type: files
Name: {app}\geotiff.dll; Type: files
Name: {app}\libmysql.dll; Type: files
Name: {app}\vistrails; Type: filesandordirs
Name: {app}\vistrails\packages\gridfield; Type: filesandordirs
Name: {app}\lib\site-packages; Type: filesandordirs
[Run]
Filename: {tmp}\vcredist_{#bits}.exe; Parameters: /Q; Components: ; Tasks: 


[ThirdPartySettings]
CompileLogFile=Output\build.log
CompileLogMethod=append

[PreCompile]
Name: "C:\{#python}\python.exe"; Parameters: "C:\Users\vistrails\code\vistrails\scripts\dist\windows\Input\download_usersguide.py"; Flags: abortonerror cmdprompt

[PreCompile]
Name: "C:\{#python}\python.exe"; Parameters: "-m compileall C:\Users\vistrails\code"; Flags: abortonerror cmdprompt

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

[InnoIDE_Settings]
LogFile=Output\build.log
LogFileOverwrite=false

[InnoIDE_PreCompile]
Name: C:\{#python}\python.exe; Parameters: C:\Users\vistrails\code\vistrails\scripts\dist\windows\Input\download_usersguide.py; Flags: AbortOnError CmdPrompt; 