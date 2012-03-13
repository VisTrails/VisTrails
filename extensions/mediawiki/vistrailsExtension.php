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

$wgExtensionFunctions[] = 'registerVistrailTag';
$wgExtensionCredits['parserhook'][] = array(
    'name' => 'VistrailTag',
    'author' => 'VT',
    'url' => 'http://www.vistrails.org/',
);

$resp_result = '';
function registerVistrailTag() {
    global $wgParser;
    $wgParser->setHook('vistrail', 'printVistrailTag');
}

function printVistrailTag($input,$params) {
    global $PATH_TO_IMAGES, $WEB_PATH_TO_IMAGES, $URL_TO_GRAPHS,
            $PATH_TO_GRAPHS, $VT_HOST, $VT_PORT, $USE_LOCAL_VISTRAILS_SERVER,
            $USE_VISTRAILS_XML_RPC_SERVER, $PATH_TO_VISTRAILS, $URL_TO_DOWNLOAD,
            $DB_HOST, $DB_NAME, $DB_PORT;
    $host = $DB_HOST;
    $dbname = $DB_NAME;
    $username = "vtserver";
    $vtid = "";
    $version = "";
    $port = $DB_PORT;
    $version_tag = "";
    $execute = "False";
    $showspreadsheetonly = "False";
    $force_build = 'False';
    $embedWorkflow = 'False';
    $includeFullTree = 'False';
    $forceDB = 'False';
    $showTree = 'False';
    $showWorkflow = 'False';
    foreach ($params as $key=>$value) {
        if($key == "vtid")
            $vtid = $value;
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
                $version = get_version_from_response($response);
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
        if ($key == 'showworkflow')
            $showWorkflow = $value;
        if ($key == 'showtree')
            $showTree = $value;
    }

    $linkParams = "getvt=" . $vtid . "&version=" . $version . "&db=" .$dbname .
                  "&host=" . $host . "&port=" . $port . "&tag=" .
                  $version_tag . "&execute=" . $execute .
                  "&showspreadsheetonly=" . $showspreadsheetonly .
                  "&embedWorkflow=" . $embedWorkflow . "&includeFullTree=" .
                  $includeFullTree . "&forceDB=" . $forceDB;
        
    if (strcasecmp($showTree,'True') == 0){
        $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid);
        $filename = 'vistrails/'.$filename . ".png";
        //this request is cached only on the server side
        $request = xmlrpc_encode_request("get_vt_graph_png", array($host, $port, 
                                  $dbname, $vtid, $USE_LOCAL_VISTRAILS_SERVER));
        $response = do_call($VT_HOST,$VT_PORT,$request);
        $result = clean_up($response, $filename);

        list($width, $height, $type, $attr) = getimagesize($PATH_TO_GRAPHS . $result);
        if ($width > 400)
           $width = 400;
        $res = '<a href="'.$URL_TO_DOWNLOAD.'?' . $linkParams . '">';
        $res = $res . '<img src="'. $URL_TO_GRAPHS . $result.
                        "\" alt=\"vt_id:$vtid\" width=\"$width\"/>";
        $res = $res . '</a>';
        return($res);
    }

    elseif (strcasecmp($showWorkflow,'True') == 0){
        $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid . '_' . $version);
        $filename = 'workflows/'.$filename . ".png";
        $fullpath = $PATH_TO_GRAPHS. $filename;
        $cached = file_exists($fullpath);
        if($USE_LOCAL_VISTRAILS_SERVER or 
           (!$cached or strcasecmp($force_build,'True') == 0)) {
            $request = xmlrpc_encode_request("get_wf_graph_png", array($host, 
                                         $port, $dbname, $vtid, $version, 
                                         $USE_LOCAL_VISTRAILS_SERVER));
            $response = do_call($VT_HOST,$VT_PORT,$request);
            $result = clean_up($response, $filename);
        } else {
            $result = $filename;
        }
        list($width, $height, $type, $attr) = getimagesize($PATH_TO_GRAPHS . $result);
        if ($width > 400)
           $width = 400;
        $res = '<a href="'.$URL_TO_DOWNLOAD.'?' . $linkParams . '">';
        $res = $res . '<img src="'. $URL_TO_GRAPHS . $result.
                        "\" alt=\"vt_id:$vtid version:$version\" width=\"$width\"/>";
        $res = $res . '</a>';
        return($res);
    }

    else {
        $result = '';
        $destdir = $PATH_TO_IMAGES;
        $destversion = $host . '_'. $dbname .'_' . $port . '_' .$vtid . '_' . $version;
        $destversion = md5($destversion);
        $destdir = $destdir . $destversion;
        $build_always_bool = False;
        if (strcasecmp($force_build,'True') == 0)
            $build_always_bool = True;
        if((!path_exists_and_not_empty($destdir)) or strcasecmp($force_build,'True') == 0) {
            if(!file_exists($destdir)){
                mkdir($destdir,0770);
                chmod($destdir, 0770);
            }
            if(!$USE_VISTRAILS_XML_RPC_SERVER){
                chdir($PATH_TO_VISTRAILS);
                $setVariables = 'export PATH=$PATH:/usr/bin/X11;export HOME=/var/lib/wwwrun; export TEMP=/tmp; export DISPLAY=localhost:1.0; export LD_LIBRARY_PATH=/usr/local/lib;';

                $mainCommand = 'python vistrails.py -b -e '. $destdir.' -t ' .
                           $host . ' -r ' . $port . ' -f ' . $dbname . ' -u ' .
                           $username . ' "' . $vtid .':' . $version .'"';
                $result = exec($setVariables.$mainCommand . ' 2>&1', $output, $result);
            }
            else {
                $request = xmlrpc_encode_request('run_from_db',
                                                 array($host, $port, $dbname, $vtid,
                                                       $destdir, $version, False, '',
                                                       $build_always_bool, '',
                                                       $USE_LOCAL_VISTRAILS_SERVER));
                $response = do_call($VT_HOST,$VT_PORT,$request);
                $result = multiple_clean_up($response, $destdir);
            }
        }
    }
    $files = scandir($destdir);
    $n = sizeof($files);
    if($n > 2){
        $res = '<a href="'.$URL_TO_DOWNLOAD.'?' . $linkParams . '">';
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

function get_version_from_response($xmlstring){
    try{
        $node = @new SimpleXMLElement($xmlstring);
        return (string) $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->int[0];
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

function multiple_clean_up($xmlstring, $destdir=""){
    global $USE_LOCAL_VISTRAILS_SERVER;
    try{
        $node = @new SimpleXMLElement($xmlstring);
        //var_dump($node);
        if ($USE_LOCAL_VISTRAILS_SERVER)
            return $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->string[0];
        else{
            $contents = $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->struct[0];
            foreach ($contents as $value){                                                                                                                  
                $image_name = (string) $value->name[0];                                               
                $image_contents = (string) $value->value[0]->base64[0];                               
                $fileHandle = fopen($destdir.'/'. $image_name, 'wb') or die("can't open file");       
                fputs($fileHandle, base64_decode($image_contents));                                   
                fclose($fileHandle);                                                                  
             }                                                                                       
             return $destdir;                                                                        
        }                                                                                                                                                                                    
  } catch(Exception $e) {                                                                     
    echo "bad xml";                                                                           
  }                                       
}
?>
