/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script da funcionalidad para completar de forma correcta los campos
 pertenecientes a la boleta de deposito.
 */

$(document).ready(function(){
	$('.boleta').numeric();
	$('.boleta').change(function(){
		if ($(this).val() == ''){
			$(this).val('0');		
		}
		$(this).closest('div').effect("highlight", {}, 3000);
		$('#id_total').val('0');
		jQuery.each($('.boleta'),function(index,elemento){
			if (elemento.value == '') {
				return;
			}
			$('#id_total').val(String(parseInt($('#id_total').val()) + parseInt(elemento.value)));			
		});
		$('#id_total').effect("highlight", {}, 3000);
	});
});
