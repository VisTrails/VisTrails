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

// This file will execute vistrails and return a page containing the images
// generated.
// The url should follow this format:
// run_vistrails.php?host=vistrails.org&db=vistrails&vt=8&version=598
// host and dbname are optional and you can set the default values below
// if the port is different from the dafault you can also pass the new value on
// the url
//functions.php is located inside the ./mediawiki folder
require_once 'functions.php';
require_once 'config.php';

$SUPPORTED_IMAGE_FILES = array("png", "jpg", "gif");

// set variables with default values
$host = $DB_HOST;
$port = $DB_PORT;
$dbname = $DB_NAME;
$vtid = '';
$version = '';
$username = "vtserver";
$version_tag = '';
$force_build = 'False';
$pdf= 'False';
$showtree = 'False';
$showworkflow = 'False';

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
        $version = get_version_from_response($response);
    }
}
if(array_key_exists('buildalways',$_GET))
    $force_build = $_GET['buildalways'];

if(array_key_exists('pdf',$_GET))
    $pdf = $_GET['pdf'];
if(array_key_exists('showworkflow',$_GET))
    $showworkflow = $_GET['showworkflow'];

if(array_key_exists('showtree',$_GET))
    $showtree = $_GET['showtree'];

//echo $force_build;

//Check if vtid and version were provided
if(($vtid != '' and $version != '') or
  ($vtid != '' and strcasecmp($showtree,'True') == 0)){
    $pdf_bool = False;
    $pdf_tag = '';
    if (strcasecmp($pdf,'True') == 0){
        $pdf_bool = True;
        $pdf_tag = '_pdf';
    }
    $build_always_bool = False;
    if (strcasecmp($force_build,'True') == 0)
        $build_always_bool = True;
    if (strcasecmp($showtree,'True') == 0){
        $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid);
        if ($pdf_bool == True){
            $func = "get_vt_graph_pdf";
            $filename = 'vistrails/'.$filename . ".pdf";
        } else {
            $func = "get_vt_graph_png";
            $filename = 'vistrails/'.$filename . ".png";
        }
        $request = xmlrpc_encode_request($func, array($host,
                                                      $port,
                                                      $dbname,
                                                      $vtid,
                                                      $USE_VISTRAILS_XML_RPC_SERVER));
        $response = do_call($VT_HOST,$VT_PORT,$request);
        $result = clean_up($response, $filename);
        if ($pdf_bool == True)
            $res = '<a href="' . $URL_TO_GRAPHS . $result .
                            '">' . $result . '</a>';
        else
            $res = '<img src="'. $URL_TO_GRAPHS . $result.
                       "\" alt=\"vt_id:$vtid\" />";
        echo $res;
    }
    elseif (strcasecmp($showworkflow,'True') == 0){
        $filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid . '_' . $version);
        if ($pdf_bool == True){
             $func = "get_wf_graph_pdf";
             $filename = 'workflows/'.$filename . ".pdf";
        } else {
             $func = "get_wf_graph_png";
             $filename = 'workflows/'.$filename . ".png";
        }
        $fullpath = $PATH_TO_GRAPHS. $filename;
        $cached = file_exists($fullpath);
        if($USE_LOCAL_VISTRAILS_SERVER or 
           (!$cached or strcasecmp($force_build,'True') == 0)) {
            $request = xmlrpc_encode_request($func, array($host,
                                                          $port,
                                                          $dbname,
                                                          $vtid,
                                                          $version));
            $response = do_call($VT_HOST,$VT_PORT,$request);
            $result = clean_up($response, $filename);
        } else {
            $result = $filename;
        }
        if ($pdf_bool == True)
            $res = '<a href="' . $URL_TO_GRAPHS . $result .
                            '">' . $result . '</a>';
        else
            $res = '<img src="'. $URL_TO_GRAPHS . $result.
                       "\" alt=\"vt_id:$vtid version:$version\" />";
        echo $res;
    }
    else{
        $destdir = $PATH_TO_IMAGES;
        $destversion = $host . '_'. $dbname .'_' . $port . '_' .$vtid . '_' .
                   $version. $pdf_tag;
        $destversion = md5($destversion);
        $destdir = $destdir . $destversion;
        $result = '';
        if((!path_exists_and_not_empty($destdir)) or strcasecmp($force_build,'True') == 0) {
            if (!file_exists($destdir)){
                mkdir($destdir);//,0770);
                chmod($destdir,0770);
            }

            $request = xmlrpc_encode_request('run_from_db',
                                         array($host, $port, $dbname, $vtid,
                                                    $destdir, $version, $pdf_bool,
                                                    '', $build_always_bool, '',
                                                    $USE_LOCAL_VISTRAILS_SERVER));
            $response = do_call($VT_HOST,$VT_PORT,$request);
            $result = multiple_clean_up($response, $destdir);
            //echo $result;
        }
       $files = scandir($destdir);
       $n = sizeof($files);
       if ($n > 2){
          $res = '';
          foreach($files as $filename) {
             if($filename != '.' and $filename != '..'){
                $info = pathinfo($filename);
                if ( in_arrayi($info['extension'],$SUPPORTED_IMAGE_FILES)){
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
}
else{
    echo "ERROR: Vistrails id or version not provided.\n";
}

function get_version_from_response($xmlstring){
    try{
        $node = @new SimpleXMLElement($xmlstring);
        return $node->params[0]->param[0]->value[0]->int[0];
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
