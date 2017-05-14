/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

 El siguiente script esconde el id de un producto,
 y recarga el nombre del producto para la promocion
 al seleccionarlo en el pop up
 * */

$(document).ready(function(){
	
	$(".vForeignKeyRawIdAdminField").attr("style","display:none")

	//Hack al script del admin ;)
	dismissRelatedLookupPopup = function(win, chosenId) {

		var name = windowname_to_id(win.name);

	    var elem = document.getElementById(name);

	    if (elem.className.indexOf('vManyToManyRawIdAdminField') != -1 && elem.value) {

	        elem.value += ',' + chosenId;

	    } else {

	       document.getElementById(name).value = chosenId;
	       
	       $.ajax({
	    	   url: "/admin/info_producto/"+chosenId+"/",
	    	   cache: false,
	    	   success: function(html){
	    	   $('#'+name).parent().children("strong").remove()
	    	   $('#'+name).parent().append('<strong>'+html+'</strong>');
	    	   }
	    	 });

	    }

	    win.close();

	}

});
