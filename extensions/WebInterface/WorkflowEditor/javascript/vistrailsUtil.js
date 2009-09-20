// This code prevents browser users from highlighting text when they click and drag the cursor.
// Crucial for pages that have zoom and pan functionality including workflow and vistrail viewers 

function disabletext(e){
return false
}

function reEnable(){
return true
}

//if the browser is IE4+
document.onselectstart=new Function ("return false")

//if the browser is NS6
if (window.sidebar){
	document.onmousedown=disabletext
	document.onclick=reEnable
}

function getParamFromURL(url, paramName) {

	var urlQuery = url.split("?")[1];
	var params = urlQuery.split("&");

	for ( p in params ) {
		var nameAndValue = params[p].split("=");
		if ( nameAndValue[0] == paramName ) {
			return nameAndValue[1];
		}
	}

	return false;
}

function drawLightVistrail() {

	$("#canvas").html("");

	var vistrailHTML = "Vistrail: " + vistrail.name + "<br>";

	var smallTree = vistrail.tree;
	var smallTreeNodes = vistrail.smallTreeNodes;
	//var boundingBoxValues = smallTree.boundingBox();

	var nodeString = "";

	var nodes = vistrail.treeLayout.tree.nodes;

	for ( var n in nodes ) {
		var node = nodes[n];
		nodeString += "<div id='blackBoundary-" + n + "' " +
				"style='position: absolute; " +
				"border: 1px black solid; background-color: #FFFFFF;" +
				"width: " + ( zoomLevel * ( node.width + 36 ) ) + "px; " +
				"height: " + ( zoomLevel * ( node.height + 26 ) ) + "px; " +
				"left: " + ( screenCenterX + ( zoomLevel * ( node.x - 18 - ( node.width / 2 ) ) ) ) + "px; " +
				"top: " + ( screenCenterY + ( zoomLevel * ( node.y - 13 - ( node.height / 2 ) ) ) ) + "px;'></div>";
	}

	$("#canvas").append( nodeString );

}

function drawLightWorkflow() {

	$( "#modulesViewport" ).remove(); // Clear modules

	// Draw Modules:
	var xOffset = Math.round( screenCenterX );
	var yOffset = Math.round( screenCenterY );

	var modulesHTML = "<div id='modulesViewport'>";

	for ( var i in modules ) {

		modulesHTML += "<div class='moduleDiv' id='moduleId-" + modules[i].id + "' class='module' style='position:absolute;left:" + ( screenCenterX + ( Math.round( parseFloat( modules[i].location.x ) / zoomLevel ) ) ) + "px;" +
				"top:" + ( screenCenterY - ( Math.round( parseFloat( modules[i].location.y ) / zoomLevel ) ) ) + "px;'>";

		modulesHTML += "<table class='module'" +
				" style='height:" + Math.round( 50 / zoomLevel ) + "px;'>" +
				"<tr><td colspan='2'><div class='moduleName' style='font-size: " +  ( 24 / zoomLevel )  + "px; text-align: center;'>&nbsp;&nbsp;" + ( modules[i].label ? ( modules[i].label + "<div style='font-size: " +  ( 8 / zoomLevel )  + "px;'>(" + modules[i].name + ")</div>" ) : modules[i].name ) + "</div></td></tr>" +
				"</table>" +
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
