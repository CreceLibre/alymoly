/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

Permite la búsqueda dinámica en una tabla.

 */
$(document).ready(function(){
	$('table#tabla_turnos tbody tr').quicksearch({
	  position: 'before',
	  attached: 'table#tabla_turnos',
	  stripeRowClass: ['row1', 'row2'],
	  labelText: '<img alt="Search" src="/media/img/icon_searchbox.png"/>',
	  formId:'changelist-search',
	  inputText: 'Buscar...',
	  loaderText: '<img alt="Search" src="/media/img/ajax-loader.gif"/>'

	});

	$('#changelist-search').append('<span style="float:right"><label for="id_proveedor" class="required inline">'+
            'Tipo Resumen : </label>'+
			'<select id="id_resumen" name="tipo_resumen" style="width: 230px;">'+
			'<option selected="selected" value="todos">GENERAL</option>'+
			'<option value="afectos">PRODUCTOS AFECTOS</option>'+
			'<option value="exentos">PRODUCTOS EXENTOS</option>'+
			'<option value="promociones">PROMOCIONES</option>'+
			'<option value="devoluciones">DEVOLUCIONES</option>'+
			'</select><span>'+
            '<label for="id_proveedor" class="required inline"> Formato : </label>'+
			'<select id="id_formato" name="formato" style="width: 230px;">'+
			'<option selected="selected" value="html">HTML</option>'+
			'</select><span>'
			)

	$('.qs_input').keydown(function(e) {
		if(e.keyCode == 13) {
			return false;
		}
	});
})
