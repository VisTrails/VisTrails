$(document).ready(function() {

	$("vistrail").each( function(){
		if ( $(this).attr('vistrailid') ) {
			$(this).html(
				"<iframe src='http://www.vistrails.org/webInterface/VistrailWidget.html?id=" + $(this).attr('vistrailid') + "' width='" + $(this).attr('width') + "' height='" + $(this).attr('height') + "'><p>Vistrail Viewer Requires iframes</p></iframe>"
			);
		}
	});

	$("workflow").each( function(){ 

		if ( $(this).attr('vistrailid') && $(this).attr('workflowid') ) {
			$(this).html(
				"<iframe src='http://www.vistrails.org/webInterface/WorkflowWidget.html?vt=" + $(this).attr('vistrailid') + "&version=" + $(this).attr('workflowid') + "' width='" + $(this).attr('width') + "' height='" + $(this).attr('height') + "'><p>Vistrail Viewer Requires iframes</p></iframe>"
			);
		}
	});
});

