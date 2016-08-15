/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script recarga vía ajax el stock actual, cuando es seleccionada una bodega
  
 */

$(document).ready(function(){
	
	$('#my_form').submit(function(e){
		bodega = $("#id_bodega option:selected").text();
		valor = $('#id_valor_reinicio').val()
		return confirm('La bodega "'+bodega+'" sera reiniciada con el valor "'+valor+'". Desea continuar?')
	})

})
