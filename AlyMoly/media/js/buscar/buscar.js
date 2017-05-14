/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script busca productos a medida que se escriba texto en el campo de búsqueda
  
 */
var buscar_productos = function(){
		
		bodega = $('select#id_bodega')
		$.blockUI({ 			message: "<h1>Buscando productos...</h1>", css: { 

            border: 'none', 
            padding: '15px', 
            backgroundColor: '#000', 
            '-webkit-border-radius': '10px', 
            '-moz-border-radius': '10px', 
            opacity: .5, 
            color: '#fff' 
        } });
	       $.ajax({
	    	   url: "/admin/inventario/buscar/"+bodega.val()+"/",
	    	   data:'texto='+$('#id_texto').val(),
	    	   type: 'POST',
	    	   success: function(html){
	    	   $('#inventario-actual').html(html)
	    	   $.unblockUI();
	    	   actualiza_existencias();
	    	   },
	       	error: function (XMLHttpRequest, textStatus, errorThrown) {
	    		   $.unblockUI();
	    		 }

	    	 });
	}

$(document).ready(function(){
	
	$('#id_texto').keydown(function(e){
		if(e.keyCode == 13) {
			if($(this).val() == '')
				cargar_productos();
			else
				buscar_productos();
			
			}
		//Al usar la pistola lectora de codigo de barra, finaliza con un caracter tab, se omite
		//la acci—n por defecto de tab
		if(e.keyCode == 9) return false;
		}


	 )

})
