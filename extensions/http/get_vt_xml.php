<?php
////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2006-2011, University of Utah. 
// All rights reserved.
// Contact: contact@vistrails.org
//
// This file is part of VisTrails.
//
// "Redistribution and use in source and binary forms, with or without 
// modification, are permitted provided that the following conditions are met:
//
//  - Redistributions of source code must retain the above copyright notice, 
//    this list of conditions and the following disclaimer.
//  - Redistributions in binary form must reproduce the above copyright 
//    notice, this list of conditions and the following disclaimer in the 
//    documentation and/or other materials provided with the distribution.
//  - Neither the name of the University of Utah nor the names of its 
//    contributors may be used to endorse or promote products derived from 
//    this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
// THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
// PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
// CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
// EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
// PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
// OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
// WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
// OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
// ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
//
////////////////////////////////////////////////////////////////////////////

// This file will connect to vistrails XML RPC server and return a vistrail in
// xml format
// The url should follow this format:
// get_vt_xml.php?host=vistrails.org&db=vistrails&vt=8
// host and dbname are optional and you can set the default values below
// if the port is different from the dafault you can also pass the new value on
// the url
//functions.php is located inside the ./mediawiki folder
require_once 'functions.php';
require_once 'config.php';

// set variables with default values
$host = $DB_HOST;
$port = $DB_PORT;
$dbname = $DB_NAME;
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
