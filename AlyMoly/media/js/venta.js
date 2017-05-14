/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog’as Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script contien todas las funcionas javascript necesaria
 para hacer funcionar venta.
  
 */

$(document).ready(function(){
	//cargo cuerpo correspondiente a la venta
	$('body').load('/venta/cuerpo_venta/');
	$.blockUI.defaults.applyPlatformOpacityRules = false;
})
