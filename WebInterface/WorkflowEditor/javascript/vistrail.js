var vistrail = new Object();
vistrail.taggedActions = new Array();

$(document).ready(function() {
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
			$('tag', xml).each( function(){

				var taggedAction = new Object();

				taggedAction.id = $(this).attr("id");
				taggedAction.name = $(this).attr("name");

				vistrail.taggedActions[taggedAction.id] = taggedAction;
			});
			drawVistrail();
		}
	});
});

function drawVistrail() {

	$("Title").html( "Vistrail - " + vistrail.name  );

	var vistrailHTML = "Vistrail: " + vistrail.name + "<br>";

	for ( var ta in vistrail.taggedActions ) {
		vistrailHTML += "<a href='http://www.vistrails.org/extensions/get_wf_xml.php?host=vistrails.sci.utah.edu&port=3306&db=vistrails&vt=" + vistrail.id + "&version=" + vistrail.taggedActions[ta].id + "'>" + 
				vistrail.taggedActions[ta].name + 
				"</a><br>";
	}

	$("#canvas").html( vistrailHTML );
}
