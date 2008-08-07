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

$wgExtensionFunctions[] = 'registerVistrailTag';
$wgExtensionCredits['parserhook'][] = array(
	'name' => 'VistrailTag',
	'author' => 'VT',
	'url' => 'http://vistrails.sci.utah.edu/',
);

 
function registerVistrailTag() {
	global $wgParser;
	$wgParser->setHook('vistrail', 'printVistrailTag');
}
 
function printVistrailTag($input,$params, &$parser) {
	$parser->disableCache();
	$path =  "vistrails.py";
	$serverPath = "";
	$dbname = "";
	$username = "vtserver";
	$vtid = "";
	$version = "";

	foreach ($params as $key=>$value) {
		if($key == "vtid")
			$vtid = "".$value;
		if($key == "version")
			$version = $value;
		if($key == "host")
			$serverPath = $value;
		if($key == "db")
			$dbname = $value;	
	}    
   	
	chdir('/server/wiki/vistrails/main/vistrails/trunk/vistrails');
	//$curdir =  exec("pwd")."\n";
	//echo exec("echo $DISPLAY");
	$setVariables = 'export PATH=$PATH:/usr/bin/X11;export HOME=/var/lib/wwwrun; export TEMP=/tmp; export DISPLAY=localhost:1.0; export LD_LIBRARY_PATH=/usr/local/lib;';
	$destdir = '/server/wiki/vistrails/main/images/vistrails/';
	$destversion = $dbname . '_' .$vtid . '_' . $version;
	$destversion = md5($destversion);
	$destdir = $destdir . $destversion;
	//echo $destdir;
	if(!file_exists($destdir)) {
	    mkdir($destdir,0770);
	    $mainCommand = 'python ' . $path . ' -b -e '. $destdir.' -t ' . $serverPath . ' -f ' . $dbname . ' -u ' . $username . ' "' . $vtid .':' . $version .'"';
	    //echo $mainCommand."\n";
	    $result = exec($setVariables.$mainCommand . ' 2>&1', $output, $result);
	    //echo $result."\n";
	}
	$linkParams = "getvt=" . $vtid . "&version=" . $version . "&db=" .$dbname;
	$files = scandir($destdir);
	$res = '<a href="http://www.vistrails.org/extensions/download.php?' . $linkParams . '">';
	foreach($files as $filename) {
	    if($filename != '.' and $filename != '..'){
		list($width, $height, $type, $attr) = getimagesize($destdir.'/'.$filename);
		if ($width > 350)
		   $width = 350;
	        $res = $res . '<img src="/images/vistrails/'. $destversion.'/'.$filename. "\" alt=\"vt_id:$vtid version:$version\" width=\"$width\"/>";
	    }
	}
	$res = $res . '</a>';
	return($res);
}
?>
