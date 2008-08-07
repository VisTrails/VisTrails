<?php
////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2006-2008 University of Utah. All rights reserved.
//
// This file is part of VisTrails.
//
// This file may be used under the terms of the GNU General Public
// License version 2.0 as published by the Free Software Foundation
// and appearing in the file LICENSE.GPL included in the packaging of
// this file.  Please review the following to ensure GNU General Public
// Licensing requirements will be met:
// http://www.opensource.org/licenses/gpl-license.php
//
// If you are unsure which license is appropriate for your use (for
// instance, you are interested in developing a commercial derivative
// of VisTrails), please contact us at vistrails@sci.utah.edu.
//
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
//
////////////////////////////////////////////////////////////////////////////

// This file will execute vistrails and return a page containing the images 
// generated.
// The url should follow this format:
// run_vistrails.php?host=vistrails.sci.utah.edu&db=vistrails&vt=8&version=598
// host and dbname are optional and you can set the default values below
// if the port is different from the dafault you can also pass the new value on
// the url

// Change this to point to the folder where vistrails.py is 
$PATH_TO_VISTRAILS = '/server/wiki/vistrails/main/vistrails/trunk/vistrails';

// Change this to point to the folder where the images should be generated
$PATH_TO_IMAGES = '/server/wiki/vistrails/main/images/vistrails/';

// set variables with default values
$host = 'vistrails.sci.utah.edu';
$port = '3306';
$dbname = 'vistrails';
$vtid = '';
$version = '';
$username = "vtserver";

//Get the variables from the url
if(array_key_exists('host', $_GET))
	$host = $_GET['host'];
if(array_key_exists('db',$_GET))
	$dbname = $_GET['db'];
if(array_key_exists('port',$_GET))
	$port = $_GET['port'];
if(array_key_exists('vt',$_GET))
	$vtid = $_GET['vt'];
if(array_key_exists('version',$_GET))
	$version = $_GET['version'];

//Check if vtid and version were provided
if($vtid != '' and $version != ''){
	chdir($PATH_TO_VISTRAILS);
	//$curdir =  exec("pwd")."\n";
	//echo exec("echo $DISPLAY");
	$setVariables = 'export PATH=$PATH:/usr/bin/X11;export HOME=/var/lib/wwwrun; export TEMP=/tmp; export DISPLAY=localhost:1.0; export LD_LIBRARY_PATH=/usr/local/lib;';
	$destdir = $PATH_TO_IMAGES;
	$destversion = $host . '_'. $dbname .'_' . $port . '_' .$vtid . '_' . $version;
	$destversion = md5($destversion);
	$destdir = $destdir . $destversion;
	//echo $destdir;
	$result = '';
	if(!file_exists($destdir)) {
	    mkdir($destdir,0770);
	    $mainCommand = 'python vistrails.py -b -e '. $destdir.' -t ' . $host .
		' -r ' . $port . ' -f ' . $dbname . ' -u ' . $username . ' "' . $vtid .
		':' . $version .'"';
	    //echo $mainCommand."\n";
	    $result = exec($setVariables.$mainCommand . ' 2>&1', $output, $result);
	    //echo $result."\n";
	}
	$files = scandir($destdir);
	$n = sizeof($files);
	if ($n > 2){
		$res = '';
		foreach($files as $filename) {
			if($filename != '.' and $filename != '..'){
				list($width, $height, $type, $attr) = getimagesize($destdir.'/'.$filename);
					$res = $res . '<img src="/images/vistrails/'. $destversion.'/'.$filename.
					        "\" alt=\"vt_id:$vtid version:$version\" width=\"$width\"/>";
			}
		}	
		echo $res;
	}
	else{
		echo "ERROR: Vistrails didn't produce any image.\n";
		echo "This is the output: \n".$result;
	}
}
else{
	echo "ERROR: Vistrails id or version not provided.\n";
}
?>
