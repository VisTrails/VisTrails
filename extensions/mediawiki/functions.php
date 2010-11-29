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

function in_arrayi($needle, $haystack) {
    return in_array(strtolower($needle), array_map('strtolower', $haystack));
}

function path_exists_and_not_empty($path){
    $directory_not_empty = FALSE;
	if (file_exists($path)){
		$directory = dir($path);
	
		while ((FALSE !== ($item = $directory->read())) && 
		   ( ! $directory_not_empty)){
			// If an item is not "." and "..", then something
	    	// exists in the directory and it is not empty
	    	if ($item != '.' && $item != '..'){
		  		$directory_not_empty = TRUE;
			}
		}
		$directory->close();
	}
	return $directory_not_empty;
}

?>
