/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog’as Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script contiene todas las funciones javascript necesarias
 para hacer funcionar el proceso de venta.
  
 */
$(document).ready(function(){
	var prefix = '/devolucion';
	$.ajax({
		url: prefix + "/cabecera/",
		cache: false,
		dataType: 'json',
		success: function(data_){
			$('#fecha-devolucion').html(data_['fecha_devolucion']);
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			mensaje_error(XMLHttpRequest.responseText);
			$("input:text:visible").focus();
		}
	});				
	$("#cantidad").numeric();
	$('#codigo-barra').focus();
	$("#codigo-barra").keypress(function(e) {
		/**
		 * Se maneja la pulsaci—n de la tecla tab ya que la lectora de c—digos
		 * de barra luego de leer agrega una tabulaci—n al flujo.
		 */
		switch (e.keyCode) {
			case 9:
				$("#formulario-elemento").submit();
				return false;
				break;
		}
		return true;
	});
	$("#formulario-elemento").submit(function(){
		if ($('#codigo-barra').val() == ""){
			return false;
		}
		$.ajax({
			url: prefix + "/elemento/" + $("#codigo-barra").val() + '/',
			cache: false,
			dataType: 'json',
			success: function(data_){
				$('#formulario-elemento').hide();
				$('#codigo-barra').val('');
				$('#elemento-descripcion').html(data_['descripcion']);
				$('#elemento-precio').html(data_['precio']);
				$('#formulario-detalle').show();
				$("#cantidad").val('');
				$("#cantidad").focus();
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				mensaje_error(XMLHttpRequest.responseText);
				$("input:text:visible").focus();
			}
		});		
		return false;
	});
	$("#formulario-detalle").submit(function(){
		if ($('#cantidad').val() == ''){
			$('#cantidad').focus();
			return false;
		}
		$.ajax({
			url: prefix + "/elemento/add/" + $('#cantidad').val() + "/",
			cache: false,
			dataType: 'json',
			success: function(data_){
				$('#formulario-detalle').hide();
				$('#cantidad').val('');
				$('#detalle-vacio').hide();
				$('#elementos-devolucion').show();
				if ($("#elementos-devolucion-" + data_['elemento']['codigo']).length == 0) {
					var fila = construir_fila(data_);
					$('#elementos-devolucion tbody').append(fila);
				}
				else{
					var fila = $("#elementos-devolucion-" + data_['elemento']['codigo']);
					$(fila).find(".cantidad").html(data_['elemento']['cantidad']);
					$(fila).find(".precio_total").html(data_['elemento']['precio_total']);					
				}
				$('#detalle-devolucion').show();
				$('#formulario-devolucion').show();				
				$("#boton-devolucion").focus();
				$('#buscador-detalle').hide();
				$(fila).effect("highlight", {}, 3000);
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				mensaje_error(XMLHttpRequest.responseText);
				$("input:text:visible").focus();
			}
		});
		return false;					
	});
	$('#boton-devolucion').click(function(){
		generar_devolucion();
		return false;
	})
	$('#a-cancelar-devolucion').click(function(){
		interfas_inicial();
		return false;
	})
	$("#a-agregar").click(function(){
		/**
		 * Se maneja el env’o del formulario para que se 
		 * agrega la existencia al detalle de la venta.
		 */
		$("#formulario-detalle").submit();
		return false;
	});
	$("#a-cancelar").click(function(){
		/**
		 * Se maneja la interacci—n del evento click para cambiar
		 * de contenido el div actual, ya que el usuario ha cancelado
		 * la selecci—n del producto.
		 */		
		$('#codigo_barra').val('');
		$('#formulario-elemento').show();
		$('#formulario-detalle').hide();
		$('#codigo-barra').focus();
		return false;
	});	
});
