////// GLOBAL VARIABLES //////
var activeTool;  // 1 for Pan, and 2 for Zoom
var startedLine;
var positionSource = new Object();
var positionDestination = new Object();
var jg;
var startedLine = false;

var screenWidth = 0, screenHeight = 0, screenCenterX = 0, screenCenterY = 0;
var previousScreenCenterX = 0;
var previousScreenCenterY = 0;

var zoomLevel = 2.0;
var previousZoomLevel = 2.0;

// Workflow Variables:
var modules = new Array();
var lastModuleId = 0;
var lastModuleLocationId = 0;
var lastConnectionId = 0;
var connections = new Array();

var moduleInputPorts = new Array();
var moduleOutputPorts = new Array();

function setModuleLocation( module, node ) {
	module.location = new Object();

	module.location.id = $(node).attr("id");
	lastModuleLocationId = Math.max( parseInt( module.location.id ), lastModuleLocationId );

	module.location.x = $(node).attr("x");
	module.location.y = $(node).attr("y");
}

function setConnectionPort(connection, node) {

	if ( $(node).attr("type") == "source" ) {
		connection.source.id = $(node).attr("id");
		connection.source.moduleId = $(node).attr("moduleId");
		connection.source.moduleName = $(node).attr("moduleName");
		connection.source.name = $(node).attr("name");
		connection.source.spec = $(node).attr("spec");

		if ( moduleOutputPorts[connection.source.moduleId] ) {
			moduleOutputPorts[connection.source.moduleId][moduleOutputPorts[connection.source.moduleId].length] = connection.source;
		} else {
			moduleOutputPorts[connection.source.moduleId] = new Array();
			moduleOutputPorts[connection.source.moduleId][0] = connection.source;
		}

	} else if ( $(node).attr("type") == "destination" ) {
		connection.destination.id = $(node).attr("id");
		connection.destination.moduleId = $(node).attr("moduleId");
		connection.destination.moduleName = $(node).attr("moduleName");
		connection.destination.name = $(node).attr("name");
		connection.destination.spec = $(node).attr("spec");

		if ( moduleInputPorts[connection.destination.moduleId] ) {
			moduleInputPorts[connection.destination.moduleId][moduleInputPorts[connection.destination.moduleId].length] = connection.source;
		} else {
			moduleInputPorts[connection.destination.moduleId] = new Array();
			moduleInputPorts[connection.destination.moduleId][0] = connection.source;
		}

	}
}

$(document).ready(function() {

	getWindowDimensions();
	screenCenterX = screenWidth / 2;
	screenCenterY = screenHeight / 2;

	// Bind events for changing active tool

	activeTool = 1;
	$("#panButton").attr("border","1px");

	$("#panButton").mousedown(function(e){
		activeTool = 1;
		$("#panButton").attr("border","1px");
		$("#zoomButton").attr("border","0px");
	});

	$("#zoomButton").mousedown(function(e){
		activeTool = 2;
		$("#panButton").attr("border","0px");
		$("#zoomButton").attr("border","1px");
	});

	$("#executeButton").mousedown(function(e){
		window.open('http://www.vistrails.org/extensions/run_vistrails.php?host=vistrails.sci.utah.edu&port=3306&db=vistrails&vt=' + getParamFromURL( "" + window.location, "vt" ) + "&version=" + getParamFromURL( "" + window.location, "version" ),'','scrollbars=no,menubar=no,height=600,width=800,resizable=yes,toolbar=no,location=no,status=no');
	});

	jg = new jsGraphics("canvas");    // Use the "canvas" div for drawing
	jg.setColor("#000000");

	// bind user interaction events

	$("#canvas").mousedown( function(e) {
		positionSource.x = e.pageX;
		positionSource.y = e.pageY;

		previousScreenCenterX = screenCenterX;
		previousScreenCenterY = screenCenterY;

		previousZoomLevel = zoomLevel;

		if ( activeTool != 0 ) {
			startedLine = true;
		}
	}).mousemove(function(e){
		if ( startedLine ) {
			if ( activeTool == 1 ) pan(e);
			if ( activeTool == 2 ) zoom(e);
		}
	}).mouseup(function(e){
		startedNewConnection = false;
		outputPortNode = null;
		inputPortNode = null;

		if ( startedLine ) {
			positionDestination.x = e.pageX;
			positionDestination.y = e.pageY;
			startedLine = false;
		}

		drawWorkflow();
	});

	$.ajax({
	    url: "http://www.vistrails.org/extensions/get_wf_xml.php?host=vistrails.sci.utah.edu&port=3306&db=vistrails&vt=" + getParamFromURL( "" + window.location, "vt" ) + "&version=" + getParamFromURL( "" + window.location, "version" ),
	    type: 'GET',
	    dataType: 'xml',
	    timeout: 1000,
	    error: function(){
		alert('Error loading XML document');
	    },
	    success: function(xml){

		$('module', xml).each(function(){

			module = new Object();

			module.name = $(this).attr("name");
			module.id = $(this).attr("id");
			module.package = $(this).attr("package");
			module.namespace = $(this).attr("namespace");

			lastModuleId = Math.max( parseInt( module.id ), lastModuleId );

			modules[module.id] = module;

			$(this).find('location').each(function(){
				var node = this;
				setModuleLocation(module, node);
			});

			module.label = "";
		});

		$( 'connection', xml ).each(function(){
			var i = connections.length;

			connections[i] = new Object();
			connection = connections[i];

			connection.id = $(this).attr("id");
			lastConnectionId = Math.max( parseInt( connection.id ), lastConnectionId );

			connection.selected = false;

			connection.source = new Object();
			connection.destination = new Object();

			$(this).find('port').each(function(){
				var node = this;
				setConnectionPort(connection, node);
			});
		});
		drawWorkflow();
	    }
	});
});

function pan(e) {

	screenCenterX = previousScreenCenterX + ( ( e.pageX - positionSource.x ) );
	screenCenterY = previousScreenCenterY + ( ( e.pageY - positionSource.y ) );

	drawLightWorkflow();
}

function zoom(e) {

	// Add something about a reference center point that matches the screen center point.  Zoom about this point

	var sign = parseFloat( e.pageY - positionSource.y  );
	var magnitude = Math.abs(sign);
	sign = sign / magnitude;

	magnitude /= 200.0;
	magnitude++;

	if ( sign > 0 ) zoomLevel = previousZoomLevel * magnitude;
	else zoomLevel = previousZoomLevel / magnitude;

	drawLightWorkflow();
}

function drawWorkflow() {

	jg.clear(); // Clear connections
	$( "#modulesViewport" ).remove(); // Clear modules

	// Draw Modules:
	var xOffset = Math.round( screenCenterX );
	var yOffset = Math.round( screenCenterY );

	var modulesHTML = "<div id='modulesViewport'>";

	for ( var i in modules ) {

		modulesHTML += "<div class='moduleDiv' id='moduleId-" + modules[i].id + "' class='module' style='position:absolute;left:" + ( screenCenterX + ( Math.round( parseFloat( modules[i].location.x ) / zoomLevel ) ) ) + "px;" +
				"top:" + ( screenCenterY - ( Math.round( parseFloat( modules[i].location.y ) / zoomLevel ) ) ) + "px;'>";

		modulesHTML += "<table " + ( modules[i].selected ? "class='selectedModule'" : "class='module'" );

		modulesHTML += " style='height:" + Math.round( 50 / zoomLevel ) + "px;'><tr><td>" + getInputs( modules[i].id ) + "</td></tr>" +
				"<tr><td colspan='2'><div class='moduleName' style='font-size: " +  ( 24 / zoomLevel )  + "px; text-align: center;'>&nbsp;&nbsp;" + ( modules[i].label ? ( modules[i].label + "<div style='font-size: " +  ( 8 / zoomLevel )  + "px;'>(" + modules[i].name + ")</div>" ) : modules[i].name ) + "</div></td></tr>" +
				"<tr><td colspan='2'>" + getOutputs( modules[i].id ) + "</td></tr></table>" +
				"</div>";
	}

	modulesHTML += "</div>";

	$("#canvas").html( modulesHTML );

	// Draw connections:

	var strokeWidth =  Math.round( 4 / zoomLevel );
	strokeWidth = ( strokeWidth < 1 ? 1 : strokeWidth );
	jg.setStroke( strokeWidth );

	var sourcePosition;
	var destinationPosition;

	for (var i in connections) {
		if ( document.getElementById( "output|" + connections[i].source.moduleId + "|" + connections[i].source.spec ) ) {
			sourcePosition = findPos( document.getElementById( "output|" + connections[i].source.moduleId + "|" + connections[i].source.spec ) );
			destinationPosition = findPos( document.getElementById( "input|" + connections[i].destination.moduleId + "|" + connections[i].source.spec ) );
			jg.setClassName('c-' + i);

			if ( connections[i].selected ) {
				jg.setColor("#FF9900");
			} else jg.setColor("#000000");

			jg.drawLine( sourcePosition.x, sourcePosition.y, destinationPosition.x, destinationPosition.y );
			jg.setClassName(null);
		}
	}
	jg.paint();
}

function getInputs(moduleId) {

	var module = modules[moduleId];
	var inputArray = moduleInputPorts[moduleId];

	var inputTableString = "<table class='inputRack'><tr><td>";

	for ( var i in inputArray ) {
		inputTableString += "<div class='inputPort' " +
				    "moduleID='" + moduleId + "' " +
				    "id='input|" + moduleId + "|" + inputArray[i].spec + "'" +
				    "style='border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;'>" +
				    "</div></td><td>";
	}

	return inputTableString + "</td></td></table>";
}

function getOutputs(moduleId) {

	var module = modules[moduleId];
	var outputArray = moduleOutputPorts[moduleId];

	var outputTableString = "<table class='outputRack'><tr><td>";
	
	for ( var i in outputArray ) {
		outputTableString += "<div class='outputPort' " +
				    "moduleID='" + moduleId + "' " +
				    "id='output|" + moduleId + "|" + outputArray[i].spec + "'" +
				    "style='border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;'>" +
				    "</div></td><td>";
	}

	return outputTableString + "</td></td></table>";
}

function findPos( obj ) {

	var curleft = curtop = 0;

	if (obj.offsetParent) {
		do {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;
		} while (obj = obj.offsetParent);
	}

	var position = new Object();
	position.x = curleft + ( 7 / zoomLevel );
	position.y = curtop + ( 6 / zoomLevel );

	return position;

}

function findLocation(obj) {

	var curleft = curtop = 0;

	if (obj.offsetParent) {
		do {
			curleft += obj.offsetLeft;
			curtop += obj.offsetTop;
		} while (obj = obj.offsetParent);
	}

	var position = new Object();
	position.x = curleft;
	position.y = curtop;

	return position;

}

