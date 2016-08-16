/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script recarga vía ajax el stock crítico, cuando es seleccionada una bodega
  
 */
var cargar_productos = function(){
		
		bodega = $('select#id_bodega')
		$.blockUI({ 			message: "<h1>Cargando productos...</h1>", css: { 

            border: 'none', 
            padding: '15px', 
            backgroundColor: '#000', 
            '-webkit-border-radius': '10px', 
            '-moz-border-radius': '10px', 
            opacity: .5, 
            color: '#fff' 
        } });
	       $.ajax({
	    	   url: "/admin/inventario/critico/"+bodega.val()+"/",
	    	   success: function(html){
	    	   $('#stock-critico').html(html)
	    	   $.unblockUI();
	    	   },
	       	error: function (XMLHttpRequest, textStatus, errorThrown) {
	    		   $.unblockUI();
	    		 }

	    	 });
	}

$(document).ready(function(){
	
	$('select#id_bodega').change(function(e){
		if($('select#id_bodega').val() == '')
			$('#stock-critico').html('')
		else
			cargar_productos();
		
		}
	 )
	 
	 if($('select#id_bodega').val() != ''){cargar_productos();}
})
