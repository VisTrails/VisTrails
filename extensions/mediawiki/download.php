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

require_once 'functions.php';
require_once 'config.php';
 
if (array_key_exists('getvt', $_GET)) {
	
    $host = $DB_HOST;
    $port = $DB_PORT;
    $dbname = $_GET["db"];
    $vtid = $_GET["getvt"];
    $version = $_GET["version"];
    $version_tag = '';
    $execute = 'False';
    $showspreadsheetonly = 'False';
    $forceDB = 'False';
    $includeFullTree = 'False';
    $embedWorkflow = 'False';
  
    if(array_key_exists('port', $_GET))
        $port = $_GET['port'];
    if(array_key_exists('host', $_GET))
        $host = $_GET['host'];
    if(array_key_exists('tag', $_GET))
        $version_tag = $_GET['tag'];
    if(array_key_exists('execute', $_GET))
        $execute = $_GET['execute'];
    if(array_key_exists('showspreadsheetonly', $_GET))
        $showspreadsheetonly = $_GET['showspreadsheetonly'];
    if(array_key_exists('forceDB', $_GET))
        $forceDB = $_GET['forceDB'];
    if(array_key_exists('includeFullTree', $_GET))
        $includeFullTree = $_GET['includeFullTree'];
    if(array_key_exists('embedWorkflow', $_GET))
        $embedWorkflow = $_GET['embedWorkflow'];
        
    $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid . '_' . $version);
    $filename = $filename . ".vtl";
	
    //change the address below to appropriate folder 
    //(with read+write access to apache user) if required
    $fileHandle = fopen($PATH_TO_IMAGES. $filename, 'w') or die("can't open file");
    $text = '<vtlink database="' . $dbname . '" host="'. $host .
            '" port="'. $port . '" vtid="' . $vtid . '" execute="'.
            $execute . '" showSpreadsheetOnly="'. $showspreadsheetonly.
            '" forceDB="'.$forceDB.'"';
    if(strcasecmp($embedWorkflow, 'True') == 0){
        if (strcasecmp($includeFullTree,'True') == 0){
           $request = xmlrpc_encode_request('get_vt_zip', array($host, $port,
                                                                $dbname, $vtid));
           $response = do_call($VT_HOST,$VT_PORT,$request);
           $vtcontent = get_vt_from_response($response);
           $text .= ' version="' . $version . '" tag="' . $version_tag .'"';
           //echo $vtcontent;
        }
        else{
           $request = xmlrpc_encode_request('get_wf_vt_zip', array($host, $port,
                                                                $dbname, $vtid,
                                                                $version)); 
           $response = do_call($VT_HOST,$VT_PORT,$request);
           $vtcontent = get_vt_from_response($response);
           //when a workflow is embedded the version is written only when
           //forceDB is True. Or else version points to the wrong workflow
           if (strcasecmp($forceDB, 'True') == 0){
                $text .= ' version="' . $version . '" tag="' . $version_tag .'"';
           }
        }
        $text .= ' vtcontent="'.$vtcontent .'"';
    }
    else{
        $text .= ' version="' . $version . '" tag="' . $version_tag .'"';
    }
    $text .= ' />';  
    fputs($fileHandle, $text);
    fclose($fileHandle);
  
    header("Content-Type: text/vistrails");
    header("Content-Disposition: attachment;filename=" . $filename);

    //the address below should be the same as one above in line 12
    readfile($PATH_TO_IMAGES.$filename);
    exit();
}
function get_vt_from_response($xmlstring) {
    try{
        $node = @new SimpleXMLElement($xmlstring);
        return $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->string[0];
    } catch(Exception $e) {
        echo "bad xml";
    }
}
?>

<html>
<head>
<title>Vistrails Download</title>
<body>

Wrong parameters set!

</body>
</html>
<? //Ends ?>

