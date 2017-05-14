/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script enlaza el evento de click en caja de texto de fecha,
 para garillar el selector de fecha de jquery ui
  
 */

$(document).ready(function(){
	$('.tipo_fecha').datepicker({dateFormat: 'dd/mm/yy', maxDate: '+0D'});

	}
)
