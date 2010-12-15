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

// This file will connect to vistrails XML RPC server and return a vistrail in
// xml format
// The url should follow this format:
// get_vt_xml.php?host=vistrails.sci.utah.edu&db=vistrails&vt=8
// host and dbname are optional and you can set the default values below
// if the port is different from the dafault you can also pass the new value on
// the url
//functions.php is located inside the ./mediawiki folder
require_once 'functions.php';
require_once 'config.php';

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
	//echo $host . $port . $dbname . $vtid . $destdit . $version;
    $request = xmlrpc_encode_request('get_vt_xml',
 	                                  array($host, $port, $dbname, $vtid));
	$response = do_call($VT_HOST,$VT_PORT,$request);
	$response = html_entity_decode($response);
	header("Content-Type: text/xml");
	clean_up($response);
}
else{
	echo "ERROR: Vistrails id not provided.\n";
}

function clean_up($xmlstring){
    try{
	   $node = new SimpleXMLElement($xmlstring);
	   echo '<?xml version="1.0"?> '."\n";
	   echo $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->string[0]->vistrail[0]->asXML();
    } catch(Exception $e) {
        echo "bad xml";
    }
}
?>
