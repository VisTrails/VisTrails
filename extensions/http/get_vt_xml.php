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

// This is where vistrails XML-RPC is running
$USE_VISTRAILS_XML_RPC_SERVER = True;

$VT_HOST = "vistrails.sci.utah.edu";
$VT_PORT = 8080;

// Change this to point to the folder where vistrails.py is 
// You won't need this if $USE_VISTRAILS_XML_RPC_SERVER is set to True
$PATH_TO_VISTRAILS = '/server/wiki/vistrails/main/vistrails/v1.2/vistrails';

// Change this to point to the folder where the images should be generated
$PATH_TO_IMAGES = '/server/wiki/vistrails/main/images/vistrails/';

// Change this to the web accessible path to the folder where the images were generated
$WEB_PATH_TO_IMAGES = '/images/vistrails/';

// set variables with default values
$host = 'vistrails.sci.utah.edu';
$port = '3306';
$dbname = 'vistrails';
$vtid = '';
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

//Check if vtid was provided
//echo $vtid;
if($vtid != ''){
    if($USE_VISTRAILS_XML_RPC_SERVER){
	   //echo $host . $port . $dbname . $vtid . $destdit . $version;
	   $request = xmlrpc_encode_request('get_vt_xml',
                                         array($host, $port, $dbname, $vtid));
	   $response = do_call($VT_HOST,$VT_PORT,$request);
	   $response = html_entity_decode($response);
	   header("Content-Type: text/xml");
	   clean_up($response);
    }
}
else{
	echo "ERROR: Vistrails id not provided.\n";
}

function clean_up($xmlstring){
    try{
	   $node = new SimpleXMLElement($xmlstring);
	   echo '<?xml version="1.0"?> '."\n";
	   echo $node->params[0]->param[0]->value[0]->string[0]->vistrail[0]->asXML();;
    } catch(Exception $e) {
        echo "bad xml";
    }
}

function do_call($host, $port, $request) {
 
    $url = "http://$host:$port/";
    $header[] = "Content-type: text/xml";
    $header[] = "Content-length: ".strlen($request);
   
    $ch = curl_init();  
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $request);
   
    $data = curl_exec($ch);      
    if (curl_errno($ch)) {
        print curl_error($ch);
    } else {
        curl_close($ch);
        return $data;
    }
}

?>
