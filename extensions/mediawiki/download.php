<?
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
if ($_GET["getvt"]) {
	$port = '3306';
	$host = 'vistrails.sci.utah.edu';
	$dbname = $_GET["db"];
	$vtid = $_GET["getvt"];
	$version = $_GET["version"];
    $version_tag = '';
    $execute = "False";
    $showspreadsheetonly = "False";
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
	$filename = md5($host . '_'. $dbname .'_' . $port .'_' .$vtid . '_' . $version);
	$filename = $filename . ".vtl";
	
	//change the address below to appropriate folder 
	//(with read+write access to apache user) if required
	$fileHandle = fopen("/server/wiki/vistrails/main/images/vistrails/". $filename, 'w') or die("can't open file");
	$text = "<vtlink database=\"" . $dbname . "\" host=\"". $host .
	        "\" port=\"". $port . "\" vtid=\"" . $vtid . "\" version=\"" .
			$version . "\" tag=\"" . $version_tag . "\" execute=\"".
            $execute . "\" showSpreadsheetOnly=\"". $showspreadsheetonly .
            "\" />";

	fputs($fileHandle, $text);
	fclose($fileHandle);

	header("Content-Type: text/vistrails");
	header("Content-Disposition: attachment;filename=" . $filename);

	//the address below should be the same as one above in line 12
	readfile("/server/wiki/vistrails/main/images/vistrails/".$filename);
	exit();
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

