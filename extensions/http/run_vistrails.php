<?php
////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2006-2010 University of Utah. All rights reserved.
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
//functions.php is located inside the ./mediawiki folder
require_once 'functions.php';
require_once 'config.php';

// This is where vistrails XML-RPC is running
$USE_VISTRAILS_XML_RPC_SERVER = True;

$SUPPORTED_IMAGE_FILES = array("png", "jpg", "gif");

// set variables with default values
$host = 'vistrails.sci.utah.edu';
$port = '3306';
$dbname = 'vistrails';
$vtid = '';
$version = '';
$username = "vtserver";
$version_tag = '';
$force_build = 'False';
$pdf= 'False';

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
if(array_key_exists('tag',$_GET)){
	$version_tag = $_GET['tag'];
	if ($version_tag != ''){
		$request = xmlrpc_encode_request('get_tag_version',array($host, $port,
																 $dbname, $vtid,
																 $version_tag));
		$response = do_call($VT_HOST,$VT_PORT,$request);
		$version = get_result_from_response($response);
	}
}
if(array_key_exists('buildalways',$_GET))
	$force_build = $_GET['buildalways'];
	
if(array_key_exists('pdf',$_GET))
    $pdf = $_GET['pdf'];
//echo $force_build;

//Check if vtid and version were provided
if($vtid != '' and $version != ''){
    $pdf_option = '';
    $pdf_bool = False;
    $pdf_tag = '';
    if (strcasecmp($pdf,'True') == 0){
        $pdf_option = '-p ';
        $pdf_bool = True;
        $pdf_tag = '_pdf';
    }
	$destdir = $PATH_TO_IMAGES;
	$destversion = $host . '_'. $dbname .'_' . $port . '_' .$vtid . '_' .
	               $version. $pdf_tag;
	$destversion = md5($destversion);
	$destdir = $destdir . $destversion;
	$result = '';
	if((!file_exists($destdir)) or strcasecmp($force_build,'True') == 0) {
		if (!file_exists($destdir)){
			mkdir($destdir);//,0770);
			chmod($destdir,0770);
		}
		if(!$USE_VISTRAILS_XML_RPC_SERVER){
			chdir($PATH_TO_VISTRAILS);
			//$curdir =  exec("pwd")."\n";
			//echo exec("echo $DISPLAY");
			$setVariables = 'export PATH=$PATH:/usr/bin/X11;export HOME=/var/lib/wwwrun; export TEMP=/tmp; export DISPLAY=localhost:1.0; export LD_LIBRARY_PATH=/usr/local/lib;';
			$mainCommand = 'python vistrails.py -b -e '. $pdf_option . $destdir.' -t ' .
							$host .' -r ' . $port . ' -f ' . $dbname . ' -u ' .
							$username . ' "' . $vtid . ':' . $version .'"';
			//echo $mainCommand."\n";
			$result = exec($setVariables.$mainCommand . ' 2>&1', $output, $result);
		}
		else {
			$request = xmlrpc_encode_request('run_from_db',
											 array($host, $port, $dbname, $vtid,
													$destdir, $version, $pdf_bool));
			$response = do_call($VT_HOST,$VT_PORT,$request);
			$result = get_result_from_response($response);
			//echo $result;
		}
	}
	$files = scandir($destdir);
	$n = sizeof($files);
	if ($n > 2){
		$res = '';
		foreach($files as $filename) {
			if($filename != '.' and $filename != '..'){
				$info = pathinfo($filename);
				if ( in_array($info['extension'],$SUPPORTED_IMAGE_FILES)){ 
				    list($width, $height, $type, $attr) = getimagesize($destdir.'/'.$filename);
				    if ($width > 600)
                        $width = 600;
				    $res = $res . '<img src="'. $WEB_PATH_TO_IMAGES . $destversion.'/'.$filename.
					   "\" alt=\"vt_id:$vtid version:$version\" width=\"$width\"/>";
			    }
				else{
					//create an href tag
					$res = $res . '<a href="' . $WEB_PATH_TO_IMAGES . 
					        $destversion.'/'.$filename.'">' . $filename . '</a>';
				}
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

function get_result_from_response($response) {
	function contents($parser, $data){
		global $resp_result;
	    $result = $data;
	}

	function  start_tag($parser, $data){
         //do nothing
	} 

	function end_tag($parser, $data){
		//do nothing
	}
	$resp_result = '';
	$xml_parser = xml_parser_create();
	xml_set_element_handler($xml_parser, "start_tag", "end_tag");
	xml_set_character_data_handler($xml_parser, "contents");
	if(!(xml_parse($xml_parser, $response, True))){
		die("Error on line " . xml_get_current_line_number($xml_parser));	
	}
	xml_parser_free($xml_parser);
	return $resp_result;
}

?>
