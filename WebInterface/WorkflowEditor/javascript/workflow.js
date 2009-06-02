////// GLOBAL VARIABLES //////
var activeTool;  // 0 for Select, 1 for Pan, and 2 for Zoom
var startedLine;
var positionSource = new Object();
var positionDestination = new Object();
var jg;
var jg1;
var startedLine = false;
var startedNewConnection = false;
var outputPortNode = null;
var inputPortNode = null;
var testingstring = '';

var screenWidth = 0, screenHeight = 0, screenCenterX = 0, screenCenterY = 0;
var previousScreenCenterX = 0;
var previousScreenCenterY = 0;

var zoomLevel = 1.0;
var previousZoomLevel = 1.0;

// Registry Variables:
var registry = new Array(); // an array of packages.  Each package contains modules and each module contains its port specs.
var moduleDescriptors = new Array();

var moduleDescriptorsByPackageIdentifier = new Array();

var constantSigstrings = new Array();

// Workflow Variables:
var modules = new Array();
var lastModuleId = 0;
var lastModuleLocationId = 0;
var lastConnectionId = 0;
var connections = new Array();

var connectionsByModuleId = new Array();

var moduleInputs = new Array();
var moduleOutputs = new Array();

// Shared Variables:
var moduleDescriptorIndices = new Array();  // key: package:name|namespace value: index of this module descriptor in the registry array

// Functions:

function setModulePortSpec(portSpecs, node) {
	var j = portSpecs.length;
	portSpecs[j] = new Object();

	portSpec = portSpecs[j];

	portSpec.id = $(node).attr("id");
	portSpec.name = $(node).attr("name");
	portSpec.optional = $(node).attr("optional");
	portSpec.sigstring = $(node).attr("sigstring");
	portSpec.sortKey = $(node).attr("sortKey");
	portSpec.type = $(node).attr("type");
}

function addModuleDescriptor(node) {

	var moduleDescriptor = new Object();

	moduleDescriptor.baseDescriptor = $(node).attr("baseDescriptorId");
	moduleDescriptor.id = $(node).attr("id");
	moduleDescriptor.name = $(node).attr("name");
	moduleDescriptor.namespace = $(node).attr("namespace");
	moduleDescriptor.package = $(node).attr("package");

	moduleDescriptors[ moduleDescriptor.id ] = moduleDescriptor;

	var length = moduleDescriptorsByPackageIdentifier[ moduleDescriptor.package ].length;
	moduleDescriptorsByPackageIdentifier[ moduleDescriptor.package ][ length ] = moduleDescriptor.id;

	// package:name|namespace
	moduleDescriptorIndices[ moduleDescriptor.package + ":" + moduleDescriptor.name + "|" + moduleDescriptor.namespace ] = moduleDescriptor.id;

	if ( parseInt( moduleDescriptor.baseDescriptor ) == 1) {
		var sigstring = moduleDescriptor.package + ":" + moduleDescriptor.name;
		constantSigstrings[sigstring] = true;
	}
	moduleDescriptor.portSpecs = new Array();

	$(node).find('portSpec').each(function(){
		var node = this;
		setModulePortSpec(moduleDescriptor.portSpecs, node);
	});

}

function setModuleLocation( module, node ) {
	module.location = new Object();

	module.location.id = $(node).attr("id");
	lastModuleLocationId = Math.max( parseInt( module.location.id ), lastModuleLocationId );

	module.location.x = $(node).attr("x");
	module.location.y = $(node).attr("y");
}

function setModuleFunctions(module, node) {

	var j = module.functions.length;
	module.functions[j] =  new Object();

	module.functions[j].name = $(node).attr("name");
	module.functions[j].id = $(node).attr("id");

	module.functions[j].parameters = new Array();

	$(node).find('parameter').each(function(){
		var node = this;
		setModuleParameters(module, node, j);
	});
}

function setModuleParameters(module, node, j) {

	var k = module.functions[j].parameters.length;

	module.functions[j].parameters[k] = new Object();

	module.functions[j].parameters[k].id = $(node).attr("id");
	module.functions[j].parameters[k].name = $(node).attr("name");
	module.functions[j].parameters[k].pos = $(node).attr("pos");
	module.functions[j].parameters[k].type = $(node).attr("type");
	module.functions[j].parameters[k].val = $(node).attr("val");

}

function setConnectionPort(connection, node) {

	if ( $(node).attr("type") == "source" ) {

		connection.source.id = $(node).attr("id");
		connection.source.moduleId = $(node).attr("moduleId");
		connection.source.moduleName = $(node).attr("moduleName");
		connection.source.name = $(node).attr("name");
		connection.source.spec = $(node).attr("spec");

		// check to see if this port is optional, if so, notify the module.

		/*
			var module = modules[moduleId];
			moduleDescriptorId = moduleDescriptorIndices[ module.package + ":" + module.name + "|" + module.namespace ];
			var portSpecs = moduleDescriptors[moduleDescriptorId].portSpecs;
		*/

	} else if ( $(node).attr("type") == "destination" ) {

		connection.destination.id = $(node).attr("id");
		connection.destination.moduleId = $(node).attr("moduleId");
		connection.destination.moduleName = $(node).attr("moduleName");
		connection.destination.name = $(node).attr("name");
		connection.destination.spec = $(node).attr("spec");

		// check to see if this port is optional, if so, notify the module.
	}
}

function toggleRegistryPackage(node) {
	$(node).next().toggle();
	var oldLabel = $(node).html();
	var newLabel = ( oldLabel.indexOf('-') >= 0
			?
				'&nbsp;+' + oldLabel.substring( oldLabel.indexOf('-') + 1 )
			:
				'&nbsp;-' + oldLabel.substring( oldLabel.indexOf('+') + 1 )
			);
	$(node).html(newLabel);
}

function drawRegistry() {

	$("#registry").replaceWith('<div class="basic" style="float:left;"  id="registry"></div>');

	for ( var i in registry ) {

		var moduleListString = "";

		for ( var m in moduleDescriptorsByPackageIdentifier[ registry[i].identifier ] ) {

			var j = moduleDescriptorsByPackageIdentifier[ registry[i].identifier ][m];
			moduleListString += '<table class="treeLines"><tr><td class="treeLines">&nbsp;&nbsp;|-&nbsp;</td><td><div id="moduleTypeId' + moduleDescriptors[j].id + '" class="moduleType">' + moduleDescriptors[j].name + '</div></td></tr></table>';

		}

		$("<div id='package" + registry[i].id + "' class='package'></div>").html( '&nbsp;-&nbsp;' + registry[i].name ).appendTo('#registry');
		$("<div id='package" + registry[i].id + "modules'></div>").html( moduleListString ).appendTo('#registry');

		$( '#package' + registry[i].id ).click( function () {
			var node = this;
			toggleRegistryPackage(node);
		});

	}

	$(".moduleType").draggable({appendTo: '.canvas', helper: 'clone', revertDuration: 10000, cursor: 'move' });

};

$(document).ready(function() {

	getWindowDimensions();
	screenCenterX = screenWidth / 2;
	screenCenterY = screenHeight / 2;

	// Bind events for changing active tool

	$("body").keypress(function (e) {
		removeSelected();
	});

	activeTool = 0;
	$("#selectButton").attr("border","1px");

	$("#selectButton").mousedown(function(e){ 
		activeTool = 0;
		$("#selectButton").attr("border","1px");
		$("#panButton").attr("border","0px");
		$("#zoomButton").attr("border","0px");
	});
	
	$("#panButton").mousedown(function(e){
		activeTool = 1;
		$("#selectButton").attr("border","0px");
		$("#panButton").attr("border","1px");
		$("#zoomButton").attr("border","0px");
	});
	
	$("#zoomButton").mousedown(function(e){
		activeTool = 2;
		$("#selectButton").attr("border","0px");
		$("#panButton").attr("border","0px");
		$("#zoomButton").attr("border","1px");
	});

	jg = new jsGraphics("canvas");    // Use the "canvas" div for drawing
	jg.setColor("#000000");

	jg1 = new jsGraphics("canvas2");    // Use the "canvas2" div for drawing temporary connections
	jg1.setColor("#FFEE00");

	// bind user interaction events

	$("#canvas").mousedown(function(e){
		positionSource.x = e.pageX;
		positionSource.y = e.pageY;

		previousScreenCenterX = screenCenterX;
		previousScreenCenterY = screenCenterY;

		previousZoomLevel = zoomLevel;

		startedLine = true;

	}).mousemove(function(e){
		if ( startedNewConnection ) {
			var xOffset = ( ( e.pageX - positionSource.x < 0 ) ? 5 : -5 );
			var yOffset = ( ( e.pageY - positionSource.y < 0 ) ? 5 : -5 );
			jg1.clear();
			var strokeWidth = Math.round( 4 / zoomLevel );
			strokeWidth = ( strokeWidth < 1 ? 1 : strokeWidth );
			jg1.setStroke( strokeWidth );
			jg1.drawLine( positionSource.x, positionSource.y, e.pageX + xOffset, e.pageY + yOffset );
			jg1.paint();
		} else if ( startedLine ) {
			if ( activeTool == 0 ) drawSelect(e);
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
			if ( activeTool == 0 ) selectModules( e.shiftKey );
		}

		$("#canvas2").html('');
	});

	$("#canvas2").mouseup(function(e){

		startedNewConnection = false;
		outputPortNode = null;
		inputPortNode = null;

		if ( startedLine ) {
			positionDestination.x = e.pageX;
			positionDestination.y = e.pageY;
			//drawLine();
			startedLine = false;

			if ( activeTool == 0 ) selectModules(e.shiftKey);
		}

		$("#canvas2").html('');

	}).mousemove(function(e){
		if ( startedNewConnection ) {
			var xOffset = ( ( e.pageX - positionSource.x < 0 ) ? 5 : -5 );
			var yOffset = ( ( e.pageY - positionSource.y < 0 ) ? 5 : -5 );
			jg1.clear();
			var strokeWidth = Math.round( 4 / zoomLevel );
			strokeWidth = ( strokeWidth < 1 ? 1 : strokeWidth );
			jg1.setStroke( strokeWidth );
			jg1.drawLine( positionSource.x, positionSource.y, e.pageX + xOffset, e.pageY + yOffset );
			jg1.paint();
		} else if ( startedLine ) {
			if ( activeTool == 0 ) drawSelect(e);
			if ( activeTool == 1 ) pan(e);
			if ( activeTool == 2 ) zoom(e);
		}
	});


	// create new modules from module descriptors using drag and drop
	$(".basic.functionList").droppable({
		accept: ".moduleType",
		activeClass: 'droppable-active',
		hoverClass: 'droppable-hover',
		drop: function(ev, ui) {
		}
	});

	$(".canvas").droppable({
		accept: ".moduleType",
		activeClass: 'droppable-active',
		hoverClass: 'droppable-hover',
		drop: function(ev, ui) {

			var moduleTypeID = ( "" + ev.target.getAttribute("id")).substring(12);

			module = new Object();

			module.name = moduleDescriptors[moduleTypeID].name; // "New Module";

			lastModuleId++
			module.id = lastModuleId;
			module.package = moduleDescriptors[moduleTypeID].package;
			module.namespace = moduleDescriptors[moduleTypeID].namespace; // Someday this might hurt.
			module.selected = false;

			module.location = new Object();

			lastModuleLocationId++;
			module.location.id = lastModuleLocationId;

			module.location.x = parseFloat( ev.pageX - screenCenterX ) * zoomLevel;
			module.location.y = parseFloat( ev.pageY - screenCenterY ) * -1 * zoomLevel;

			module.functions = new Array();  // Functions not included in registry ?  How do you get functions from module descriptors?

			module.optionalPorts = new Array();
			module.annotation = "";
			module.label = "";

			modules[module.id] = module;

			drawModules();
		}
	});

	$.ajax({
	    url: 'http://kodos.eng.utah.edu/cbrooks/registry.xml',
	    type: 'GET',
	    cache: true,
	    dataType: 'xml',
	    timeout: 8446744073709551610,
	    error: function(){
		alert('Error loading XML document');
	    },
	    success: function(xml){

		$('package', xml).each( function(){

		  var pckg = new Object();
		  //registry[registry.length] = pckg;

		  pckg.codepath = $(this).attr("codepath");
		  pckg.description = $(this).attr("description");
		  pckg.id = $(this).attr("id");
		  pckg.identifier = $(this).attr("identifier");
		  pckg.loadConfiguration = $(this).attr("loadConfiguration");
		  pckg.name = $(this).attr("name");
		  pckg.version = $(this).attr("version");

		  registry[pckg.id] = pckg;

		  moduleDescriptorsByPackageIdentifier[pckg.identifier] = new Array();

		  $(this).find('moduleDescriptor').each(function(){
			  var node = this;
			  addModuleDescriptor( node );
		  });

		});

		drawRegistry();

		$.ajax({
		    url: 'workflowExample.xml',
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

				lastModuleId = Math.max( parseInt(module.id), lastModuleId );

				module.selected = false;
				modules[module.id] = module;

				$(this).find('location').each(function(){
					var node = this;
					setModuleLocation(module, node);
				});

				module.functions = new Array();

				$(this).find('function').each(function(){
					var node = this;
					setModuleFunctions(module, node);
				});

				module.optionalPorts = new Array();
				module.annotation = "";
				module.label = "";

			});

			$('connection', xml).each(function(){

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
			drawModules();

		    }
		});
	    }
	});
});

function removeSelected() {
	var tempModules = new Array();

	for ( var i in modules ) {
		if ( !modules[i].selected ) tempModules[i] = modules[i];
	}

	var tempConnections = new Array();

	for ( var i in connections ) {
		if ( tempModules[ connections[i].source.moduleId ] && tempModules[ connections[i].destination.moduleId ] && !connections[i].selected ) {
			tempConnections[i] = connections[i];
		}
	}

	modules = tempModules;
	connections = tempConnections;
	drawModules();
}

function selectModules( additive ) {

	var left = Math.min( positionDestination.x, positionSource.x );
	var top = Math.min( positionDestination.y, positionSource.y );

	var right = Math.max( positionDestination.x, positionSource.x );
	var bottom = Math.max( positionDestination.y, positionSource.y );

	$( ".moduleDiv" ).each( function(){

		var currentModule = modules[$(this).attr("id").split("-")[1]];

		if ( currentModule ) {

			if ( !additive ) currentModule.selected = false;

			var modulePostion = findLocation( document.getElementById("moduleId-" + currentModule.id) );
			var mX = modulePostion.x;
			var mY = modulePostion.y;

			if ( mX >= left && mY >= top && mX <= right && mY <= bottom ) {
				currentModule.selected = true;
			}
		}
	});

	autoSelectConnections();

	drawModules();
}

function autoSelectConnections() {

	for ( var i in connections ) {
		if ( modules[ connections[i].source.moduleId ].selected && modules[ connections[i].destination.moduleId ].selected ) {
			connections[i].selected = true;
		} //else connections[i].selected = false;
	}

}

function drawSelect(e) {

	var xS = Math.min( e.pageX, positionSource.x );
	var yS = Math.min( e.pageY, positionSource.y );

	var widthS = Math.abs( e.pageX - positionSource.x );
	var heightS = Math.abs( e.pageY - positionSource.y );

	$("#canvas2").html( "<div style='position: absolute; left: " + xS + "px; top: " + yS + "px; width: " + widthS + "px; height: " + heightS + "px; border: 2px solid #FA0;;'></div>" );
}

function pan(e) {

	screenCenterX = previousScreenCenterX + ( ( e.pageX - positionSource.x ) );
	screenCenterY = previousScreenCenterY + ( ( e.pageY - positionSource.y ) );

	drawModules();
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

	drawModules();
}

function drawModules() {

	// Clear connections
	jg.clear();
	// Clear modules
	$( "#modulesViewport" ).remove();

	// Draw Modules:

	var xOffset = Math.round( screenCenterX );
	var yOffset = Math.round( screenCenterY );

	var modulesHTML = "<div id='modulesViewport'>";

	for ( var i in modules ) {

		modulesHTML += "<div class='moduleDiv' id='moduleId-" + modules[i].id + "' class='module' style='position:absolute;left:" + ( screenCenterX + ( Math.round( parseFloat( modules[i].location.x ) / zoomLevel ) ) ) + "px;" +
				"top:" + ( screenCenterY - ( Math.round( parseFloat( modules[i].location.y ) / zoomLevel ) ) ) + "px;'>";

		modulesHTML += "<table " + ( modules[i].selected ? "class='selectedModule'" : "class='module'" );

		modulesHTML += " style='height:" + Math.round( 50 / zoomLevel ) + "px;'><tr><td>" + getInputs( modules[i].id ) + "</td><td><img src='images/arrow.png' id='options-" + modules[i].id + "' style='cursor:pointer;padding:1px;float:right;width:" + Math.round( 12 / zoomLevel ) + "px;height:" + Math.round( 16 / zoomLevel ) + "px'></td></tr>" +
				"<tr><td colspan='2'><div class='moduleName' style='font-size: " +  ( 24 / zoomLevel )  + "px; text-align: center;'>&nbsp;&nbsp;" + ( modules[i].label ? ( modules[i].label + "<div style='font-size: " +  ( 8 / zoomLevel )  + "px;'>(" + modules[i].name + ")</div>" ) : modules[i].name ) + "</div></td></tr>" +
				"<tr><td colspan='2'>" + getOutputs( modules[i].id ) + "</td></tr></table>" +
				"</div>";
	}

	modulesHTML += "</div>";

	$("#canvas").html( modulesHTML );

	// Bind drag events to modules
	$( ".moduleDiv" ).draggable({
		helper: 'original',
		opacity: '0.5',
		cursor: 'move',
		stop: function(event, ui) {
			moveModule( this, ui.position );
		}
	});

	// Select module click event
	$( ".moduleDiv" ).click(function (e) { 
		selectModule( this, e.shiftKey );
	});


	// Draw connections:

	var strokeWidth =  Math.round( 4 / zoomLevel );
	strokeWidth = ( strokeWidth < 1 ? 1 : strokeWidth );
	jg.setStroke( strokeWidth );

	var sourcePosition;
	var destinationPosition;

	for (var i in connections) {

		//alert("output|" + connections[i].source.moduleId + "|" + connections[i].source.spec + "\n" + "input|" + connections[i].destination.moduleId + "|" + connections[i].destination.spec);

		if ( document.getElementById( "output|" + connections[i].source.moduleId + "|" + connections[i].source.spec ) ) {
			sourcePosition = findPos( document.getElementById( "output|" + connections[i].source.moduleId + "|" + connections[i].source.spec ) );
			destinationPosition = findPos( document.getElementById( "input|" + connections[i].destination.moduleId + "|" + connections[i].destination.spec ) );
			jg.setClassName('c-' + i);
			if ( connections[i].selected ) {
				jg.setColor("#FF9900");
			} else jg.setColor("#000000");

			jg.drawLine( sourcePosition.x, sourcePosition.y, destinationPosition.x, destinationPosition.y );
			jg.setClassName(null);
		}
	}

	jg.paint();

	for ( var i in connections ) {
		$(".c-" + connections[i].id).mousedown(function(e){
			selectConnection( this, e.shiftKey );
		});
	}

	for ( var i in modules ) {
		$("#options-" + modules[i].id).mousedown(function(){
			if (activeTool == 0) showOptions(this);
		});
	}

	$(".outputPort").bind("mouseenter",function(){
		$( ".moduleDiv" ).draggable( 'disable' );
	}).bind("mouseleave",function(){
		if ( !startedNewConnection ) {
			$( ".moduleDiv" ).draggable( 'enable' );
		}
	});

	// Bind events for drawing new connections
	$(".outputPort").mousedown(function(e){

		//$(this).attr("id").split("|")[2];

		positionSource.x = e.pageX;
		positionSource.y = e.pageY;

		startedNewConnection = true;

		outputPortNode = new Object();
		outputPortNode.moduleID = $(this).attr("moduleID");
		outputPortNode.sigstring = $(this).attr("sigstring");

		// turn all of the inputPorts to orange.
		$(".inputPort").each( function(e){
			if ( $(this).attr("sigstring") == outputPortNode.sigstring ) {
				$(this).css("border-color","#FF9900");
			}
		});

	});

	$(".inputPort").mouseup(function(e){

		if ( startedNewConnection ) {

			$("#canvas2").html('');

			positionDestination.x = e.pageX;
			positionDestination.y = e.pageY;

			startedNewConnection = false;

			inputPortNode = new Object();
			inputPortNode.moduleID = $(this).attr("moduleID");
			inputPortNode.sigstring = $(this).attr("sigstring");

			if ( outputPortNode.sigstring == inputPortNode.sigstring ) {
				var i = connections.length;

				connections[i] = new Object();
				connection = connections[i];

				lastConnectionId++;
				connection.id = lastConnectionId;

				connection.selected = false;

				connection.source = new Object();
				connection.destination = new Object();

				connection.source.id = 10; //$(node).attr("id"); // ?
				connection.source.moduleId = outputPortNode.moduleID; //$(node).attr("moduleId");
				connection.source.moduleName = modules[outputPortNode.moduleID].name; //$(node).attr("moduleName");
				connection.source.name = "whatever"; //$(node).attr("name"); // ?
				connection.source.spec = outputPortNode.sigstring; //$(node).attr("spec");

				connection.destination.id = 10; //$(node).attr("id"); //?
				connection.destination.moduleId = inputPortNode.moduleID; //$(node).attr("moduleId");
				connection.destination.moduleName = modules[inputPortNode.moduleID].name; //$(node).attr("moduleName");
				connection.destination.name = "whatever"; //$(node).attr("name");
				connection.destination.spec = inputPortNode.sigstring; //$(node).attr("spec");
			}
		}

		inputPortNode = null;
		outputPortNode = null;

		drawModules();
	});
}

function moveModule( node, position ) {

	var id = parseInt( $(node).attr("id").split('-')[1] );

	var xDiff = (parseFloat( position.left - screenCenterX ) * zoomLevel) - parseFloat(modules[id].location.x);
	var yDiff = (parseFloat( position.top - screenCenterY ) * -1 * zoomLevel) - parseFloat(modules[id].location.y);

	if ( !modules[id].selected ) selectSingleModule(id, false);

	for ( var i in modules ) {
		if ( modules[i].selected ) {
			modules[i].location.x = parseFloat( modules[i].location.x ) + xDiff;
			modules[i].location.y = parseFloat( modules[i].location.y ) + yDiff;
		}
	}

	drawModules();
}

function selectModule( node, additive ) {

	var id = parseInt( $(node).attr("id").split('-')[1] );

	if ( !modules[id].selected ) selectSingleModule( id, additive );

	drawModules();
}

function selectSingleModule(id, additive) {

	if ( !additive ) {
		deselectAll();
		showFunctions(id);
	}

	modules[id].selected = true;

	autoSelectConnections();
}

function deselectAll() {
	for ( var i in connections ) {
		connections[i].selected = false;
	}

	for ( var i in modules ) {
		modules[i].selected = false;
	}
}

function selectConnection( node, additive ) {

	var id = parseInt( $(node).attr("class").split('-')[1] );

	if ( !additive ) {
		deselectAll();
	}

	connections[id].selected = true;
	drawModules();
}

function showOptions( node ) {

	// Harvest Mouse Coordinates
	// pick the corner to offset from
	// Draw menu

	var moduleId = node.id.split('-')[1];
	var arrowPosition = findLocation(node);

	var menuHTML = "<div id='menu-" + moduleId + "' class='menu' style='position: absolute; left: " + ( parseInt(arrowPosition.x) - 75 )  + "px; top: " + ( parseInt(arrowPosition.y) - 37 ) + "px;'>";

	// Edit Configuration
	menuHTML += "<div id='editConfiguration-" + moduleId + "' class='menuItem'>Edit Configuration</div>";

	// Annotate
	menuHTML += "<div id='annotate-" + moduleId + "' class='menuItem'>Annotate</div>";

	// Set Module Label
	menuHTML += "<div id='setModuleLabel-" + moduleId + "' class='menuItem'>Set Module Label</div>";
	menuHTML += "</div>"

	$("#menu").html( menuHTML );

	// set event bindings

	// exit the menu
	$("#menu-" + moduleId).bind( "mouseleave", function() {
		$(this).remove();
	});

	// edit configuration
	$( "#editConfiguration-" + moduleId ).click( function () {
		$("#menu").html('');
		showPortsConfiguration( this.id.split('-')[1] );
	});

	// annotate module
	$( "#annotate-" + moduleId ).click( function () {
		$("#menu").html('');
		showAnnotation( this.id.split('-')[1] );
	});

	// label module
	$( "#setModuleLabel-" + moduleId ).click( function () {
		$("#menu").html('');
		showLabel( this.id.split('-')[1] );
	});

}

function showPortsConfiguration(moduleId) {

	// Generate Form
	// Input ports, output ports, OK Button, CANCEL button

	var formHTML = "<div style='position: absolute; left: 0px; top: 100px; width: " + screenWidth + "px; height: " + ( screenHeight - 200 ) + "px; 	overflow-y: scroll;'>"
		     + "<center><div id='moduleConfiguration-" + moduleId + "' class='moduleConfiguration'>";

	// <div id='moduleConfiguration-" + moduleId + "' class='moduleConfiguration'>

	var module = modules[moduleId];

	moduleDescriptorId = moduleDescriptorIndices[ module.package + ":" + module.name + "|" + module.namespace ];

	var portSpecs = moduleDescriptors[moduleDescriptorId].portSpecs;

	var inputString = "";
	var outputString = "";

	if ( portSpecs ) {
		for ( var i in portSpecs ) {
			if ( portSpecs[i].type == "input" ) {
				if ( parseInt ( portSpecs[i].optional ) == 0 ) {
					inputString += "<input type='checkbox' class='mandatoryInputCheckbox' id='portCheckBox-" + portSpecs[i].id + "' DISABLED checked='true'>" + portSpecs[i].name + "<br>";
				} else {
					inputString += "<input type='checkbox' class='optionalInputCheckbox' id='portCheckBox-" + portSpecs[i].id + "'" + ( module.optionalPorts[portSpecs[i].id] ? " checked='true'" : "" ) + "'>" + portSpecs[i].name + "<br>";
				}
			} else {
				if ( parseInt ( portSpecs[i].optional ) == 0 ) {
					outputString += "<input type='checkbox' class='mandatoryOutputCheckbox' id='portCheckBox-" + portSpecs[i].id + "' DISABLED checked='true'>" + portSpecs[i].name + "<br>";
				} else {
					outputString += "<input type='checkbox' class='optionalOutputCheckbox' id='portCheckBox-" + portSpecs[i].id + "'" + ( module.optionalPorts[portSpecs[i].id] ? " checked='true'" : "" ) + ">" + portSpecs[i].name + "<br>";
				}
			}
		}
	}

	formHTML += "<table><tr><td style='font-weight: bold;'>Input Ports</td><td style='font-weight: bold;'>Output Ports</td></tr>" +
	            "<tr><td>" + inputString + "</td><td>" + outputString + "</td></tr>" +
		    "<tr><td><div id='changeModuleConfiguration-" + moduleId + "' class='button'>OK</div></td><td><div id='cancel' class='button'>Cancel</div></td></tr>" +
		    "</table></div></center></div>";

	$( "#menu" ).html( formHTML );

	$( "#cancel" ).click( function () {
		$( "#menu" ).html( '' );
	});

	$( "#changeModuleConfiguration-" + moduleId ).click( function () {
		changeModuleConfiguration( this.id.split('-')[1] );
		$( "#menu" ).html( '' );
	});

}

function showFunctions(moduleId) {

	var module = modules[moduleId];
	var moduleDescriptorId = moduleDescriptorIndices[ module.package + ":" + module.name + "|" + module.namespace ];

	$( "#functions" ).html(
			"<table class='treeLines'><tr><td colspan='2'><div class='methodSignature'>Method</div></td><td><div class='methodSignature'>Signature</div></td></tr>" +
			getModuleParents(moduleDescriptorId) +
			"</table>" +
			"<hr>Functions: <br>" + getModuleFunctionString(module)
		);
	$( "#functions" ).show();
	$( ".moduleDescriptorLabel" ).click( function() {
		$(".fmid" + this.id.split('-')[1]).toggle();
	});
}

//
function getModuleParents(moduleDescriptorId) {
	//baseDecriptor
	if ( parseInt( moduleDescriptorId ) >= 0 ) {
		return 	"<tr><td class='moduleDescriptorLabel' id='moduleDescriptorId-" + moduleDescriptorId + "' colspan='3'><div class='package'>" + moduleDescriptors[moduleDescriptorId].name + "</div></td></tr>" +
			getConstantPorts(moduleDescriptors[moduleDescriptorId].portSpecs, moduleDescriptorId) +
			getModuleParents(moduleDescriptors[moduleDescriptorId].baseDescriptor);
	} else return "";
}

function getModuleFunctionString(module) {

	var functionString = "";

	
	for ( var i in module.functions ) {
		functionString += module.functions[i].id + " " + module.functions[i].name + "<BR>";

		for ( var j in module.functions[i].parameters ) {
			functionString += //" -" + module.functions[i].parameters[j].id + "<BR>" +
			 		  //" -" + module.functions[i].parameters[j].name + "<BR>" +
					  //" -" + module.functions[i].parameters[j].pos + "<BR>" +
			 		  " -" + module.functions[i].parameters[j].type +
					  "<input type='text' value='" + module.functions[i].parameters[j].val + "'><BR>";
		}
	}
	return functionString;

}

function getConstantPorts( portSpecs, moduleDescriptorId ) {

	var hasMethods = false;
	var constantPortsHTML = "";

	for ( var i in portSpecs ) {

		if ( portSpecs[i].type == "input" ) {
			var sigstring = portSpecs[i].sigstring;

			if ( sigstring == "()" ) {
				hasMethods = true;
				constantPortsHTML += "<tr class='fmid" + moduleDescriptorId + "'><td class='treeLines'>&nbsp;&nbsp;&nbsp;|-</td><td><div class='methodSignature'>" + portSpecs[i].name + "</div></td><td>&nbsp;&nbsp;&nbsp;()</td></tr>";
			} else {
				var sigs = sigstring.substring(1,sigstring.length - 1).split(',');

				var tempConstantPortsString = "<tr class='fmid" + moduleDescriptorId + "'><td class='treeLines'>&nbsp;&nbsp;&nbsp;|-</td><td><div class='methodSignature'>" + portSpecs[i].name + "</div></td><td><div class='methodSignature'>&nbsp;&nbsp;&nbsp;(";

				for ( var j in sigs ) {
					if ( constantSigstrings[ sigs[j] ] ) {
						tempConstantPortsString += sigs[j].split(":")[1] + ",";
					} else {
						tempConstantPortsString = "";
						break;
					}
				}

				if ( tempConstantPortsString != "" ) {
					hasMethods = true;
					constantPortsHTML += tempConstantPortsString + ")</div></td></tr>";
				}

			}
		}
	}

	if ( hasMethods ) {
		constantPortsHTML += "";
		return constantPortsHTML;
	} else return "";
}

function changeModuleConfiguration(moduleId) {

	var optionalPorts = new Array();

	$( ".optionalInputCheckbox,.optionalOutputCheckbox" ).each( function() {
		var node = this;
		if ( node.checked ) addOptionalPorts(optionalPorts, node);
	});

	modules[moduleId].optionalPorts = optionalPorts;

	drawModules();

}

function addOptionalPorts( optionalPorts, node ) {
	optionalPorts[ node.id.split('-')[1] ] = true;
}

function showAnnotation( moduleId ) {

	// show text box
	// show save and cancel
	// bind save and cancel events

	var annotationHTML = "<div style='position: absolute; left: 0px; top: 100px; width: " + screenWidth + "px; height: " + ( screenHeight - 200 ) + "px; overflow-y: scroll;'>" +
			     "<center><div id='annotation-" + moduleId + "' class='moduleConfiguration'>";

	// <div id='moduleConfiguration-" + moduleId + "' class='moduleConfiguration'>

	var module = modules[moduleId];

	annotationHTML += "Annotation:<br><textarea id='annotationTextArea-" + moduleId + "'>" + module.annotation + "</textarea>" +
			  "<table><tr><td><div id='changeAnnotation-" + moduleId + "' class='button'>OK</div></td><td><div id='cancel' class='button'>Cancel</div></td></tr></table>" + 
			  "</div></center></div>";

	$( "#menu" ).html( annotationHTML );

	$( "#cancel" ).click( function () {
		$( "#menu" ).html( '' );
	});

	$( "#changeAnnotation-" + moduleId ).click( function () {
		changeAnnotation( this.id.split('-')[1] );
		$( "#menu" ).html( '' );
	});
}

function changeAnnotation( moduleId ) {
	modules[moduleId].annotation = $( "#annotationTextArea-" + moduleId ).attr( 'value' );
	drawModules();
}

function showLabel( moduleId ) {

//	show text box
//	show save and cancel
//	bind save and cancel events

	var module = modules[moduleId];

	var labelHTML = "<div style='position: absolute; left: 0px; top: 100px; width: " + screenWidth + "px; height: " + ( screenHeight - 200 ) + "px; overflow-y: scroll;'>" +
			"<center><div id='moduleLabel-" + moduleId + "' class='moduleConfiguration'>";

	labelHTML += "Module Label:<br><input type='text' id='moduleLabelTextBox-" + moduleId + "' value='" + module.label + "'>" +
		     "<table><tr><td><div id='changeModuleLabel-" + moduleId + "' class='button'>OK</div></td><td><div id='cancel' class='button'>Cancel</div></td></tr></table>" + 
		     "</div></center></div>";

	$("#menu").html( labelHTML );

	$( "#cancel" ).click( function () {
		$("#menu").html('');
	});

	$( "#changeModuleLabel-" + moduleId ).click( function () {
		changeModuleLabel( this.id.split('-')[1] );
		$( "#menu" ).html( '' );
	});
}

function changeModuleLabel( moduleId ) {

	modules[moduleId].label = $( "#moduleLabelTextBox-" + moduleId ).attr( 'value' );
	drawModules();

}

function getInputs(moduleId) {

	var module = modules[moduleId];
	//inspect(module);

	moduleDescriptorId = moduleDescriptorIndices[ module.package + ":" + module.name + "|" + module.namespace ];

	var portSpecs = moduleDescriptors[moduleDescriptorId].portSpecs;
	var optionalPorts = modules[moduleId].optionalPorts;

	if ( portSpecs ) {
		var inputTableString = "<table class='inputRack'><tr><td>";
		
		for ( var i in portSpecs ) {
			if ( portSpecs[i].type == "input" ) {
				if ( parseInt ( portSpecs[i].optional ) == 0 ) {
					inputTableString += "<div class='inputPort' " +
							    "moduleID='" + moduleId + "' " +
							    "sigstring='" + portSpecs[i].sigstring + "' " +
							    "id='input|" + moduleId + "|" + portSpecs[i].sigstring + "'" +
							    "style='border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;cursor:pointer;'>" +
							    "</div></td><td>";
				} else if ( optionalPorts[ portSpecs[i].id ] ) {
					inputTableString += "<div class='inputPort' " +
							    "moduleID='" + moduleId + "' " +
							    "sigstring='" + portSpecs[i].sigstring + "' " +
							    "id='input|" + moduleId + "|" + portSpecs[i].sigstring + "'" +
							    "style='-moz-border-radius:" + Math.round( 6 / zoomLevel ) + "px;-webkit-border-radius:" + Math.round( 6 / zoomLevel ) + "px;border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;'>" +
							    "</div></td><td>";
				}
			}
		}

		return inputTableString + "</td></td></table>";
	} else return "";
}

function getOutputs(moduleId) {

	var module = modules[moduleId];
	moduleDescriptorId = moduleDescriptorIndices[ module.package + ":" + module.name + "|" + module.namespace ];

	var portSpecs = moduleDescriptors[moduleDescriptorId].portSpecs;
	var optionalPorts = modules[moduleId].optionalPorts;

	if ( portSpecs ) {
		var outputTableString = "<table class='outputRack'><tr><td>";
		
		for ( var i in portSpecs ) {
			if ( portSpecs[i].type == "output" ) {
				if ( parseInt ( portSpecs[i].optional ) == 0 ) {
					outputTableString += "<div class='outputPort' " +
							    "moduleID='" + moduleId + "' " +
							    "sigstring='" + portSpecs[i].sigstring + "' " +
							    "id='output|" + moduleId + "|" + portSpecs[i].sigstring + "'" +
							    "style='border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;cursor:pointer;'>" +
							    "</div></td><td>";
				} else if ( optionalPorts[ portSpecs[i].id ] ) {
					outputTableString += "<div class='outputPort' " +
							    "moduleID='" + moduleId + "' " +
							    "sigstring='" + portSpecs[i].sigstring + "' " +
							    "id='output|" + moduleId + "|" + portSpecs[i].sigstring + "'" +
							    "style='-moz-border-radius:" + Math.round( 6 / zoomLevel ) + "px;-webkit-border-radius:" + Math.round( 6 / zoomLevel ) + "px;border: 1px solid #000;border-color:black;width: " + Math.round( 14 / zoomLevel ) + "px; height: " + Math.round( 12 / zoomLevel ) + "px;'>" +
							    "</div></td><td>";
				}
			}
		}

		return outputTableString + "</td></td></table>";
	} else return "";
}


function zoomIn() {

	if ( zoomLevel > 1 ) {
		zoomLevel = zoomLevel - 1;
	} else {
		zoomLevel = zoomLevel / 2;
	}

	drawModules();
}

function zoomOut() {

	if ( zoomLevel > 1 ) {
		zoomLevel = zoomLevel + 1;
	} else {
		zoomLevel = zoomLevel * 2;
	}

	drawModules();
}

function findPos(obj) {

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

function getWindowDimensions() {

  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    screenWidth = window.innerWidth;
    screenHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    screenWidth = document.documentElement.clientWidth;
    screenHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    screenWidth = document.body.clientWidth;
    screenHeight = document.body.clientHeight;
  }

}

function inspect(obj, maxLevels, level) {

    var str = '', type, msg;

    // Start Input Validations
    // Don't touch, we start iterating at level zero
    if(level == null)  level = 0;

    // At least you want to show the first level
    if(maxLevels == null) maxLevels = 1;
    if(maxLevels < 1)     
        return '<font color="red">Error: Levels number must be > 0</font>';

    // We start with a non null object
    if(obj == null)
    return '<font color="red">Error: Object <b>NULL</b></font>';
    // End Input Validations

    // Each Iteration must be indented
    str += '<ul>';

    // Start iterations for all objects in obj
    for(property in obj)
    {
      try
      {
          // Show "property" and "type property"
          type =  typeof(obj[property]);
          str += '<li>(' + type + ') ' + property + ' ' + obj[property] +
                 ( (obj[property]==null)?(': <b>null</b>'):('')) + '</li>';

          // We keep iterating if this property is an Object, non null
          // and we are inside the required number of levels
          if((type == 'object') && (obj[property] != null) && (level+1 < maxLevels))
          str += inspect(obj[property], maxLevels, level+1);
      }
      catch(err)
      {
        // Is there some properties in obj we can't access? Print it red.
        if(typeof(err) == 'string') msg = err;
        else if(err.message)        msg = err.message;
        else if(err.description)    msg = err.description;
        else                        msg = 'Unknown';

        str += '<li><font color="red">(Error) ' + property + ': ' + msg +'</font></li>';
      }
    }

      // Close indent
      str += '</ul>';

    $("#errors").append(str);
}
