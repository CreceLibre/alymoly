/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

Permite el enlace generación de reporte.
  
 */
$(document).ready(function(){
	$('.report-link').click(function(){
		var self = $(this);
		var url = self.attr('href') + "/" +$('select#id_formato').val()+"/"+$('select#id_resumen').val();
		window.open(url);
		return false;
	})
})