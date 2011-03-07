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

$wgExtensionFunctions[] = 'registerVistrailTag';
$wgExtensionCredits['parserhook'][] = array(
    'name' => 'VistrailTag',
    'author' => 'VT',
    'url' => 'http://vistrails.sci.utah.edu/',
);

// This is where vistrails XML-RPC is running
$USE_VISTRAILS_XML_RPC_SERVER = True;

$resp_result = '';
function registerVistrailTag() {
    global $wgParser;
    $wgParser->setHook('vistrail', 'printVistrailTag');
}

function printVistrailTag($input,$params) {
    global $PATH_TO_IMAGES, $WEB_PATH_TO_IMAGES, $URL_TO_GRAPHS,
            $PATH_TO_GRAPHS, $VT_HOST, $VT_PORT,
            $USE_VISTRAILS_XML_RPC_SERVER, $PATH_TO_VISTRAILS, $URL_TO_DOWNLOAD;
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
        $request = xmlrpc_encode_request("get_vt_graph_png", array($host, $port, $dbname, $vtid));
        $response = do_call($VT_HOST,$VT_PORT,$request);
        $result = clean_up($response);

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
        $request = xmlrpc_encode_request("get_wf_graph_png", array($host, $port, $dbname, $vtid, $version));
        $response = do_call($VT_HOST,$VT_PORT,$request);
        $result = clean_up($response);

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
                                                       $build_always_bool));
                $response = do_call($VT_HOST,$VT_PORT,$request);
                $result = clean_up($response);
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

function clean_up($xmlstring){
    try{
        $node = @new SimpleXMLElement($xmlstring);

        return $node->params[0]->param[0]->value[0]->array[0]->data[0]->value[0]->string[0];
    } catch(Exception $e) {
        echo "bad xml";
    }
}
?>
