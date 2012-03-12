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

// This file will connect to VisTrails XML RPC Server and return the url for
// the pdf file of a workflow.
// The url should follow this format:
// get_wf_pdf.php?host=vistrails.org&db=vistrails&vt=8&version=598
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
$version = '';
$username = "vtserver";
$version_tag = '';

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
        $request = xmlrpc_encode_request('get_tag_version',
                                         array($host, $port, $dbname, $vtid,
                                               $version_tag));
        $response = do_call($VT_HOST,$VT_PORT,$request);
        $version = get_version_from_response($response);
    }
}
if(array_key_exists('buildalways',$_GET))
    $force_build = (bool) $_GET['buildalways'];
        
//echo $force_build;

//Check if vtid and version were provided
//echo $vtid . $version;
if($vtid != '' and $version != ''){
    //echo $host . $port . $dbname . $vtid . $version;
    $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid . '_' . $version);
    $filename = 'workflows/'.$filename . ".pdf";
    $fullpath = $PATH_TO_GRAPHS. $filename;
    $cached = file_exists($fullpath);
    if($USE_LOCAL_VISTRAILS_SERVER or 
       (!$cached or strcasecmp($force_build,'True') == 0)) {
        $request = xmlrpc_encode_request('get_wf_graph_pdf',
                                 array($host, $port, $dbname, $vtid, $version,
                                 $USE_LOCAL_VISTRAILS_SERVER));
        //echo $request;
        $response = do_call($VT_HOST,$VT_PORT,$request);        
        $path = clean_up($response, $filename);
    } else {
        $path = $filename;
    }
    echo "$URL_TO_GRAPHS$path";
}
else{
    echo "ERROR: Vistrails id or version not provided.\n";
}

function get_version_from_response($xmlstring){
    try{
        $node = @new SimpleXMLElement($xmlstring);
        return $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->int[0];
    } catch(Exception $e) {
        echo "bad xml";
    }
}

function clean_up($xmlstring, $filename=""){
    global $PATH_TO_GRAPHS, $USE_LOCAL_VISTRAILS_SERVER;
    try{
        $node = @new SimpleXMLElement($xmlstring);
        if ($USE_LOCAL_VISTRAILS_SERVER)
            return $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->string[0];
        else{
            $contents = $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->base64[0];
            $fileHandle = fopen($PATH_TO_GRAPHS. $filename, 'wb') or die("can't open file");
            fputs($fileHandle, base64_decode($contents));
            fclose($fileHandle);
            return $filename;
        }
                  
    } catch(Exception $e) {
        echo "bad xml";
    }
}

?>
