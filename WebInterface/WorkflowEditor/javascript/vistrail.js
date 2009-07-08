var vistrail = new Object();

var positionSource = new Object();
var positionDestination = new Object();

var screenWidth = 0, screenHeight = 0, screenCenterX = 0, screenCenterY = 0;
var previousScreenCenterX = 0;
var previousScreenCenterY = 0;

var zoomLevel = 1.0;
var previousZoomLevel = 1.0;

var startedLine = false;

var jg;

$(document).ready(function() {

	getWindowDimensions();
	screenCenterX = screenWidth / 2;
	screenCenterY = screenHeight / 10;

	// Bind events for changing active tool

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

	// bind user interaction events

	$("#canvas").mousedown(function(e){
		positionSource.x = e.pageX;
		positionSource.y = e.pageY;

		previousScreenCenterX = screenCenterX;
		previousScreenCenterY = screenCenterY;

		previousZoomLevel = zoomLevel;

		startedLine = true;

	}).mousemove(function(e){
		if ( startedLine ) {
			if ( activeTool == 1 ) pan(e);
			if ( activeTool == 2 ) zoom(e);
		}
	}).mouseup(function(e){

		if ( startedLine ) {
			positionDestination.x = e.pageX;
			positionDestination.y = e.pageY;
			startedLine = false;
		}

	});


	vistrail.taggedActions = new Array();
	vistrail.actions = new Array();
	vistrail.tree = null;
	vistrail.sticks = new Array();
	var tempActions = new Array();

	$.ajax({
		url: 'http://kodos.eng.utah.edu/cbrooks/vistrailExample.xml',
		type: 'GET',
		cache: true,
		dataType: 'xml',
		timeout: 8446744073709551610,
		error: function(){
			alert('Error loading XML document');
		},
		success: function(xml){

			$('vistrail:first', xml).each( function(){
				vistrail.id = $(this).attr("id");
				vistrail.name = $(this).attr("name");
				vistrail.version = $(this).attr("version");
			});

			$('action', xml).each( function(){
				var action = new Object();
				action.id = $(this).attr("id");
				if ( action.id == 0 ) alert("found root");
				action.prevId = $(this).attr("prevId");
				action.date = $(this).attr("date");
				action.prune = $(this).attr("prune");
				action.session = $(this).attr("session");
				action.user = $(this).attr("user");
				tempActions[action.id] = action;
			});

			$('tag', xml).each( function(){

				var taggedAction = new Object();

				taggedAction.id = $(this).attr("id");
				taggedAction.name = $(this).attr("name");

				vistrail.taggedActions[taggedAction.id] = taggedAction;
			});

			var keys = new Array();

			for(k in tempActions) {
			     keys[keys.length] = k;
			}

			keys.sort( function(a, b){ return (a - b); });

			for (k in keys) {
				vistrail.actions[k] = tempActions[k];
			}


			var treeNodes = new Array();
		
			var fullTree = new Tree();
			treeNodes[0] = fullTree.addNode(null, 1, 1, "0");
		
			for ( var a in vistrail.actions ) {
				if ( a != 0 ) {
					var action = vistrail.actions[a];
					//alert(action.id + " " + a);
					if (vistrail.taggedActions[action.id]) {
						treeNodes[action.id] = fullTree.addNode(treeNodes[action.prevId], 15, 15, "" + vistrail.taggedActions[action.id].name);
					} else {
						treeNodes[action.id] = fullTree.addNode(treeNodes[action.prevId], 15, 15, "" + action.id);
					}
				}
			}

			// now create the decemated tree.
			var smallTreeNodes = new Array();

			var smallTree = new Tree();
			smallTreeNodes[0] = smallTree.addNode(null, 20, 20, "");

			for ( var id in treeNodes ) {

				if ( id != 0 && ( parseInt( treeNodes[id].getNumChildren() ) != 1 || vistrail.taggedActions[id] ) ) {

		//			if ( ( "" + treeNodes[id].getNumChildren()) == "1" ) {
					if ( ( "" + id ) == "16" ) {
						alert(  "id: " + id + " treeNodes[id]: " + treeNodes[id] + " children" + treeNodes[id].getNumChildren() +
							" taggedActions[id]: " + vistrail.taggedActions[id]);
					}

					// find its parent.
					var parentId = vistrail.actions[id].prevId;

					var count = 0;
					var stick = new Array();

					while ( parentId != 0 && treeNodes[parentId].getNumChildren() <= 1 && !vistrail.taggedActions[parentId] ) {
						stick[count] = treeNodes[parentId];
						parentId = vistrail.actions[parentId].prevId;
						count++;
					}

					// add the node to the tree.
					$("#offscreen").html( "<div id='node-" + id + "' style='position: absolute; left: -500px; top: -300px;'>" + treeNodes[id].object + "</div>" );
					smallTreeNodes[id] = smallTree.addNode(smallTreeNodes[parentId], $("#node-" + id).width(), $("#node-" + id).height(), treeNodes[id].object);

					if ( count > 0 ) {
						var stickNode = new Object();
						stickNode.expanded = false;
						stickNode.parentId = parentId;
						stickNode.childId = id;
						stickNode.stick = stick;
						vistrail.sticks[vistrail.sticks.length] = stickNode;
					}
				}
			}

			vistrail.tree = smallTree;
			vistrail.smallTreeNodes = smallTreeNodes;

			jg = new jsGraphics("canvas");
			jg.setColor("#000000");

			vistrail.treeLayout = new TreeLayout( smallTree, 0, 50, 50 );

			drawVistrail();
		}
	});
});

function drawVistrail() {

	$("Title").html( "Vistrail - " + vistrail.name  );

	$("#canvas").html("");

	var vistrailHTML = "Vistrail: " + vistrail.name + "<br>";

	var smallTree = vistrail.tree;
	var smallTreeNodes = vistrail.smallTreeNodes;
	//var boundingBoxValues = smallTree.boundingBox();

	var nodeString = "";

	var nodes = vistrail.treeLayout.tree.nodes;

	for ( var n in nodes ) {
		var node = nodes[n];
		if (node.parent != null)
			// Math.abs(boundingBoxValues[0]) +
			jg.drawLine( screenCenterX + ( zoomLevel * node.x ), screenCenterY + ( zoomLevel * node.y),
				     screenCenterX + ( zoomLevel * node.parent.x ), screenCenterY + ( zoomLevel * node.parent.y ) );

			nodeString += "<img src='images/blackCircle.gif' id='blackCircleImage-" + n + "' " +
				"width='" + ( zoomLevel * ( node.width + 36 ) ) + "'" +
				"height='" + ( zoomLevel * ( node.height + 26 ) ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX + ( zoomLevel * ( node.x - 18 - ( node.width / 2 ) ) ) ) + "px; " +
				"top: " + ( screenCenterY + ( zoomLevel * ( node.y - 13 - ( node.height / 2 ) ) ) ) + "px;'>" +

				"<img src='images/whiteCircle.gif' id='whiteCircleImage-" + n + "' " +
				"width='" + ( zoomLevel * ( node.width + 30 ) ) + "'" +
				"height='" + ( zoomLevel * ( node.height + 20 ) ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX + ( zoomLevel * ( node.x - 15 - ( node.width / 2 ) ) ) ) + "px; " +
				"top: " + ( screenCenterY + ( zoomLevel * ( node.y - 10 - ( node.height / 2 ) ) ) ) + "px;'>" +

				"<img src='images/orangeCircle.gif' id='orangeCircleImage-" + n + "' " +
				"width='" + ( zoomLevel * ( node.width + 30 ) ) + "'" +
				"height='" + ( zoomLevel * ( node.height + 20 ) ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX + ( zoomLevel * ( node.x - 15 - ( node.width / 2 ) ) ) ) + "px; " +
				"top: " + ( screenCenterY + ( zoomLevel * ( node.y - 10 - ( node.height / 2 ) ) ) ) + "px; " +
				"opacity:" + ( node.level / smallTree.maxLevel ) + ";filter:alpha(opacity=" + parseInt( node.level / smallTree.maxLevel ) + ")'>" +

				"<div id='treeAction-" + n + "' style='position: absolute; " +
				//"width: " + ( zoomLevel * node.width ) + "px; " +
				//"height: " + ( zoomLevel * node.height ) + "px; " +
				"left: " + ( screenCenterX + ( zoomLevel * ( node.x - ( node.width / 2 ) ) ) ) + "px; " +
				"top: " + ( screenCenterY + ( zoomLevel * ( node.y - ( node.height / 2 ) ) ) ) + "px; font-size: " + zoomLevel * 16 + "px;'>" + node.object + "</div>";
	}

	var sticks = vistrail.sticks;

	for ( var s in sticks ) {
		var nodeStick = sticks[ s ];
		var x = ( smallTreeNodes[ nodeStick.parentId ].x + smallTreeNodes[ nodeStick.childId ].x ) / 2.0;
		var y = ( smallTreeNodes[ nodeStick.parentId ].y + smallTreeNodes[ nodeStick.childId ].y ) / 2.0;
		nodeString += "<div class='stick' id='stick-" + s  + "' style='position: absolute; left: " + ( screenCenterX + ( zoomLevel * ( x - 6 ) ) ) + "px; top: " + ( screenCenterY + ( zoomLevel * ( y - 6 ) ) ) + "px;'><img src='images/plus.png'></div>";
	}

	jg.paint();

	$("#canvas").append( nodeString );

	$(".stick").click( function(){

		$(".stickyWidget").remove();

		var stickId =  parseInt(this.id.split('-')[1]);
		var stick = sticks[ stickId ];

		for ( var s in sticks ) {
			if ( s != stickId ) {
				sticks[s].expanded = false;
				$("#stick-" + s).html( "<img src='images/plus.png'>" );
			} //else alert(s + " " + stickId);
		}

		stick.expanded = !stick.expanded;

		if ( stick.expanded ) {
			var parentNode = smallTreeNodes[ stick.parentId ];
			var childNode = smallTreeNodes[ stick.childId ];

			var parentWidth = parentNode.width;
			var parentHeight = parentNode.height;
			var childWidth = childNode.width;
			var childHeight = childNode.height;;

			var divWidth = Math.max( parentWidth, childWidth );

			// Get the width and height of the parent and child nodes.
			// use relative positioning:
			/*
			When you position something relatively, you are modifying its position from where it would have been if you hadn't changed anything.
			*/

			var tenPercent = ( screenHeight / 10 );
			var stickHTML = "<div class='stickyWidget' style='border: 1px solid #000; background-color: rgb(221, 221, 221); " +
				"position: absolute; " +
				"width: " + ( divWidth + 44 ) + "px; " +
				"height: " + ( screenHeight * 0.85 ) + "px; " +
				"left: " + ( screenCenterX - ( ( divWidth ) / 2 ) - 22 ) + "px; " +
				"top: " + ( tenPercent - 22 ) + "px;'></div>" +

				"<img src='images/blackCircle.gif' class='stickyWidget' id='parentBlackCircleImage' " +
				"width='" + ( parentNode.width + 36 ) + "'" +
				"height='" + ( parentNode.height + 26 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( parentNode.width / 2 ) - 18 ) + "px; " +
				"top: " + tenPercent + "px;'>" +

				"<img src='images/whiteCircle.gif' class='stickyWidget' id='parentWhiteCircleImage' " +
				"width='" + ( parentNode.width + 30 ) + "'" +
				"height='" + ( parentNode.height + 20 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( parentNode.width / 2 ) - 15 ) + "px; " +
				"top: " + ( tenPercent + 3 ) + "px;'>" +

				"<img src='images/orangeCircle.gif' class='stickyWidget' id='parentOrangeCircleImage' " +
				"width='" + ( parentNode.width + 30 ) + "'" +
				"height='" + ( parentNode.height + 20 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( parentNode.width / 2 ) - 15 ) + "px; " +
				"top: " + ( tenPercent + 3 ) + "px;" +
				"opacity:" + ( parentNode.level / smallTree.maxLevel ) + "; filter:alpha(opacity=" + parseInt( parentNode.level / smallTree.maxLevel ) + ")'>" +

				"<div id='parentNode' class='stickyWidget' style='position: absolute; " +
				"left: " + ( screenCenterX - ( parentNode.width / 2 ) ) + "px; " +
				"top: " + ( tenPercent + 15 ) + "px;" +
				"font-size: 16px;'>" + parentNode.object + "</div><br>" +

			"<div id='stickView' class='stickyWidget' style='position: absolute; overflow-y: scroll;" +
			"left: " + ( screenCenterX - ( divWidth / 2 ) ) + "px; " +
			"width: " + divWidth + "px; " +
			"top: 20%; " +
			"height: 60%;'>" +
			"<table>";

			var tableHTML = "";

			for (var n in stick.stick) {
				var node = stick.stick[n];
				//$("#offscreen").html( "<div id='stickNode-" + n + "' style='position: absolute; left: -500px; top: -300px;'>" + node.object + "</div>" );
				tableHTML = "<tr><td>" + node.object + "</td></tr>" + tableHTML;
				//$("#stickNode-" + n).width()  $("#stickNode-" + n).height()
			}

			tenPercent = screenHeight - tenPercent - ( childNode.height + 26 );

			stickHTML += tableHTML + "</table></div>" + 
				"<img src='images/blackCircle.gif' class='stickyWidget' id='parentBlackCircleImage' " +
				"width='" + ( childNode.width + 36 ) + "'" +
				"height='" + ( childNode.height + 26 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( childNode.width / 2 ) - 18 ) + "px; " +
				"top: " + tenPercent + "px;'>" +

				"<img src='images/whiteCircle.gif' class='stickyWidget' id='parentWhiteCircleImage' " +
				"width='" + ( childNode.width + 30 ) + "'" +
				"height='" + ( childNode.height + 20 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( childNode.width / 2 ) - 15 ) + "px; " +
				"top: " + ( tenPercent + 3 ) + "px;'>" +

				"<img src='images/orangeCircle.gif' class='stickyWidget' id='parentOrangeCircleImage' " +
				"width='" + ( childNode.width + 30 ) + "'" +
				"height='" + ( childNode.height + 20 ) + "' " +
				"style='position: absolute; " +
				"left: " + ( screenCenterX - ( childNode.width / 2 ) - 15 ) + "px; " +
				"top: " + ( tenPercent + 3 ) + "px;" +
				"opacity:" + ( childNode.level / smallTree.maxLevel ) + "; filter:alpha(opacity=" + parseInt( childNode.level / smallTree.maxLevel ) + ")'>" +

				"<div id='parentNode' class='stickyWidget' style='position: absolute; " +
				"left: " + ( screenCenterX - ( childNode.width / 2 ) ) + "px; " +
				"top: " + ( tenPercent + 15 ) + "px;" +
				"font-size: 16px;'>" + childNode.object + "</div></div>";
			$("#canvas").append( stickHTML );
			$("#stick-" + stickId).html( "<img src='images/minus.png'>" );
		} else {
			$("#stick-" + stickId).html( "<img src='images/plus.png'>" );
			$(".stickyWidget").remove();
		}
	});
}

function pan(e) {

	screenCenterX = previousScreenCenterX + ( ( e.pageX - positionSource.x ) );
	screenCenterY = previousScreenCenterY + ( ( e.pageY - positionSource.y ) );

	drawVistrail();
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

	drawVistrail();
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
