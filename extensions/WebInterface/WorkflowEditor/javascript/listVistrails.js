// listVistrils.js retrieves XML from the vistrail server and generates html to display a
// list of vistrials stored in the database.
var vistrails = new Array();

$(document).ready(function() {

	$.ajax({
		url: 'http://www.vistrails.org/extensions/get_db_vistrail_list.php?host=vistrails.sci.utah.edu&port=3306&db=vistrails',
		type: 'GET',
		cache: true,
		dataType: 'xml',
		timeout: 8446744073709551610,
		error: function(whatever){
			inspect(whatever, 7, 0);
			alert('Error loading XML document' + " _ " + whatever.responseText);
		},

		success: function(xml){
			// <vistrail id="9" name="brain" mod_time="2009-06-17 14:45:07"/> 
			$('vistrail', xml).each(function(){

				var vistrail = new Object();
				vistrail.id = $(this).attr("id");
				vistrail.name = $(this).attr("name");
				vistrail.mod_time = $(this).attr("mod_time");
				vistrails[vistrails.length] = vistrail;
			});

			var vistrailListHTML = "";
			for ( var v in vistrails ) {
				var vistrail = vistrails[v];
				vistrailListHTML += "<a href='VistrailViewer.html?id=" + vistrail.id + "'>" + vistrail.name + "</a> " + vistrail.mod_time + "<br>";
			}

			$("#canvas").html( vistrailListHTML );
		}
	});
});

