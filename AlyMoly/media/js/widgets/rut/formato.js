/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog�as Ltda. #
#                                             #
# �Andr�s Ot�rola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

 El siguiente script formatea el R.U.T
 * */

$(document).ready(function(){
	
	$('._rut').Rut({format_on: 'change'});
	$('._rut').change();

});
