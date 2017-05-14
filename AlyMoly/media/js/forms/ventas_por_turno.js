/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog’as Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

Permite el enlace generaci—n de reporte.
  
 */
$(document).ready(function(){
	$('.report-link').click(function(){
		var self = $(this);
		var url = self.attr('href') + "/" +$('select#id_formato').val()+"/"+$('select#id_resumen').val();
		window.open(url);
		return false;
	})
})
