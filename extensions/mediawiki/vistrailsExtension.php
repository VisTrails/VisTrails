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
require_once 'functions.php';

$wgExtensionFunctions[] = 'registerVistrailTag';
$wgExtensionCredits['parserhook'][] = array(
	'name' => 'VistrailTag',
	'author' => 'VT',
	'url' => 'http://vistrails.sci.utah.edu/',
);

// This is where vistrails XML-RPC is running
$USE_VISTRAILS_XML_RPC_SERVER = True;
$VT_HOST = "localhost";
$VT_PORT = 8080;

// Change this to point to the folder where vistrails.py is 
// You won't need this if $USE_VISTRAILS_XML_RPC_SERVER is set to True
$PATH_TO_VISTRAILS = '/vistrails/v1.2/vistrails';

// Change this to point to the folder where the images should be generated
$PATH_TO_IMAGES = '/images/vistrails/';

// Change this to the web accessible path to the folder where the images were generated
$WEB_PATH_TO_IMAGES = '/images/';

$resp_result = '';
function registerVistrailTag() {
	global $wgParser;
	$wgParser->setHook('vistrail', 'printVistrailTag');
}
 
function printVistrailTag($input,$params, &$parser) {
	global $PATH_TO_IMAGES, $WEB_PATH_TO_IMAGES, $VT_HOST, $VT_PORT,
           $USE_VISTRAILS_XML_RPC_SERVER, $PATH_TO_VISTRAILS;
	$parser->disableCache();
	$host = "";
	$dbname = "";
	$username = "vtserver";
	$vtid = "";
	$version = "";
	$port = '3306';
    $version_tag = "";
    $execute = "False";
    $showspreadsheetonly = "False";
    $force_build = 'False';
    $embedWorkflow = 'False';
    $includeFullTree = 'False';
    $forceDB = 'False';
	foreach ($params as $key=>$value) {
		if($key == "vtid")
            $vtid = "".$value;
		if($key == "version")
            $version = $value;
		if($key == "host")
            $host = $value;
		if($key == "db")
            $dbname = $value;
		if($key == "port")
            $port = $value;
        if($key == "tag"){
            $version_tag = $value;
            if($version_tag != ''){
                $request = xmlrpc_encode_request('get_tag_version',
                                                 array($host, $port,
													   $dbname, $vtid,
													   $version_tag));
                $response = do_call($VT_HOST,$VT_PORT,$request);
                $version = get_result_from_response($response);
                //echo $version;
            }
        }
        if ($key == "execute")
            $execute = $value;
        if ($key == "showspreadsheetonly")
            $showspreadsheetonly = $value;
        if ($key == "buildalways")
            $force_build = $value;
        if ($key == 'embedworkflow')
            $embedWorkflow = $value;
        if ($key == 'includefulltree')
            $includeFullTree = $value;
        if ($key == 'forcedb')
            $forceDB = $value;
	}    
   
	$destdir = $PATH_TO_IMAGES;
	$destversion = $host . '_'. $dbname .'_' . $port . '_' .$vtid . '_' . $version;
	$destversion = md5($destversion);
	$destdir = $destdir . $destversion;
	//echo $destdir;
    $result = '';
	if((!file_exists($destdir)) or strcasecmp($force_build,'True') == 0) {
        if(!file_exists($destdir)){
            mkdir($destdir,0770);
            chmod($destdir, 0770);
        }
        if(!$USE_VISTRAILS_XML_RPC_SERVER){
            chdir($PATH_TO_VISTRAILS);
            //$curdir =  exec("pwd")."\n";
            //echo exec("echo $DISPLAY");
            $setVariables = 'export PATH=$PATH:/usr/bin/X11;export HOME=/var/lib/wwwrun; export TEMP=/tmp; export DISPLAY=localhost:1.0; export LD_LIBRARY_PATH=/usr/local/lib;';

            $mainCommand = 'python vistrails.py -b -e '. $destdir.' -t ' .
		               $host . ' -r ' . $port . ' -f ' . $dbname . ' -u ' .
					   $username . ' "' . $vtid .':' . $version .'"';
            //echo $mainCommand."\n";
            $result = exec($setVariables.$mainCommand . ' 2>&1', $output, $result);
            //echo $result."\n";
        }
        else{
            $request = xmlrpc_encode_request('run_from_db',
											 array($host, $port, $dbname, $vtid,
												   $destdir, $version));
			$response = do_call($VT_HOST,$VT_PORT,$request);
			$result = get_result_from_response($response);
			//echo $result;
        }
	}
	$linkParams = "getvt=" . $vtid . "&version=" . $version . "&db=" .$dbname .
				  "&host=" . $host . "&port=" . $port . "&tag=" .
                  $version_tag . "&execute=" . $execute . 
                  "&showspreadsheetonly=" . $showspreadsheetonly .
                  "&embedWorkflow=" . $embedWorkflow . "&includeFullTree=" .
                  $includeFullTree . "&forceDB=" . $forceDB;
	$files = scandir($destdir);
    $n = sizeof($files);
    if($n > 2){
        $res = '<a href="http://www.vistrails.org/extensions/download.php?' . $linkParams . '">';
        foreach($files as $filename) {
            if($filename != '.' and $filename != '..'){
                list($width, $height, $type, $attr) = getimagesize($destdir.'/'.$filename);
                if ($width > 350)
                   $width = 350;
                $res = $res . '<img src="'.$WEB_PATH_TO_IMAGES . $destversion.'/'.
                       $filename.
                       "\" alt=\"vt_id:$vtid version:$version\" width=\"$width\"/>";
            }
        }
        $res = $res . '</a>';
    }
    else{
        $res = "ERROR: Vistrails didn't produce any image.\n" .
               "This is the output: \n" . $result;
	}
	return($res);
}
function contents($parser, $data){
        global $resp_result;
        $resp_result = $resp_result . $data;
    }

    function  start_tag($parser, $data){
         //do nothing
    } 

    function end_tag($parser, $data){
        //do nothing
    }
function get_result_from_response($response) {
    global $resp_result;
    $resp_result = '';
    $xml_parser = xml_parser_create();
    xml_set_element_handler($xml_parser, "start_tag", "end_tag");
    xml_set_character_data_handler($xml_parser, "contents");
    if(!(xml_parse($xml_parser, $response, True))){
        die("Error on line " . xml_get_current_line_number($xml_parser));   
    }
    xml_parser_free($xml_parser);
    return trim($resp_result);
}
?>
