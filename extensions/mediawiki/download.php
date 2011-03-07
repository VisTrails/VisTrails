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
require_once 'config.php';
 
if (array_key_exists('getvt', $_GET)) {
	
    $port = '3306';
    $host = 'vistrails.sci.utah.edu';
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

