/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script contiene todas las funciones javascript necesarias
 para hacer funcionar el proceso de venta.
  
 */

$(document).ready(function(){
	var prefix = '/venta';
	$.ajax({
		url: prefix + "/cabecera/",
		cache: false,
		dataType: 'json',
		success: function(data_){
			modificar_datos_cabecera_turno(data_['turno']);
			modificar_datos_cabecera_venta(data_['venta']);
			if (data_['ultima_venta'] == null){
				$('#tabla-resumen-ultima-venta-span').show();			
			}
			else{
				modificar_datos_ultima_venta(data_['ultima_venta']);
			}
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			top.location.href = '/venta/';
		}
	});
	$("#cantidad").numeric();
	$('#codigo_barra').focus();
	$("#codigo_barra").keypress(function(e) {
			/**
			 * Se maneja la pulsación de la tecla tab ya que la lectora de códigos
			 * de barra luego de leer agrega una tabulación al flujo.  Además el usuario
			 * puede presionar la tecla "esc" para poder calcular el vuelto correspondiente
			 * a la venta.
			 */
			switch (e.keyCode) {
				case 9:
					if($(this).val()!='')
					$("#formulario_elemento").submit();
					return false;
					break;
				case 27:
					if (monedaToInt($("#monto-total").text())==0){
						return false;
						break;
					}
					$("#boton-calcular-vuelto").click();
					$("#vuelto-correcto").hide();
					$("#vuelto-incorrecto").hide();
					$("#vuelto-relleno").show();
					$("#vuelto-pago-cliente").val('');
					return false;
					break;
			}
			return true;
	});
	$('#cantidad').keypress(function(e){
		switch (e.keyCode){
			case 9:
				return false;
				break;
			case 13:
				if ($('#cantidad').val() == ""){
					$('#cantidad').val('1');
					$('#formulario_detalle').submit();
					return false;
				}
				return true;
		}
		return true;
	})
	$("#formulario_elemento").submit(function(){
		if ($('#codigo_barra').val() == ""){
			$("#boton-venta").click();
			return false;
		}
		$.ajax({
			url: prefix + "/elemento/" + $("#codigo_barra").val() + '/',
			cache: false,
			dataType: 'json',
			success: function(data_){
				$('#formulario_elemento').hide();
				$('#codigo_barra').val('');
				$('#elemento_descripcion').html(data_['descripcion']);
				$('#elemento_precio_venta').html(data_['precio_venta']);
				$('#formulario_detalle').show();
				$("#cantidad").val('');
				$("#cantidad").focus();
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				var existencia_error = XMLHttpRequest.getResponseHeader("existencia_error");
				var inicio_sesion = XMLHttpRequest.getResponseHeader("inicio_sesion");
				if (eval(existencia_error))
				{
					mensaje_existencia_error(XMLHttpRequest.responseText);
				}
				else{
					if (eval(inicio_sesion))
					{
						top.location.href = '/venta/';
					}
					else{
						mensaje_error(XMLHttpRequest.responseText);	
						$("input:text:visible").focus();
					}
				}
			}
		});		
		return false;
	});
	$("#formulario_detalle").submit(function(){
		if ($('#cantidad').val() == ''){
			$('#cantidad').focus();
			return false;
		}
		$.ajax({
			url: prefix + "/elemento/add/" + $('#cantidad').val() + "/",
			cache: false,
			dataType: 'json',
			success: function(data_){
				$('#formulario_detalle').hide();
				$('#cantidad').val('');
				$('#detalle-vacio').hide();
				$('#formulario_elemento').show();
				if (monedaToInt(data_['venta']['monto_total'])==0){
					$("#boton-calcular-vuelto").hide();
				}
				else{
					$("#boton-calcular-vuelto").show();					
				}
				$('#elementos-venta').show();
				if ($("#elementos-venta-" + data_['elemento']['codigo']).length == 0) {
					var fila = construir_fila(data_,$('#elementos-venta tbody tr').length);
					$('#elementos-venta tbody').append(fila);
				}
				else{
					var fila = $("#elementos-venta-" + data_['elemento']['codigo']);
					$(fila).find(".cantidad").html(data_['elemento']['cantidad']);
					$(fila).find(".precio_total").html(data_['elemento']['precio_total']);					
				}
				modificar_datos_venta(data_['venta'])
				$("#codigo_barra").focus();
				$(fila).effect("highlight", {}, 3000);
				if (data_['venta']['ultimo_tipo_elemento'] == 2){
					if ($("#box-elemento-" + data_['elemento']['codigo']).length == 0){
						var elemento = $("<div class='box-elemento' id='box-elemento-" + data_['elemento']['codigo'] + "'>");
						$(elemento).append($('<h4 class="caps">').html(data_['elemento']['descripcion']));
						jQuery.each(data_['componentes'], function(index, value){
							$(elemento).append($("<div class='quiet'>").html(value));
						})
						$('#promociones').append(elemento);
						$('#promociones .box').hide();
						$(elemento).effect("highlight", {}, 3000);			
					}
				}
				else{
					if (data_['venta']['ultimo_tipo_elemento'] == 1){
						if ($("#box-elemento-" + data_['elemento']['codigo']).length == 0) {
							var elemento = $("<div class='box-elemento' id='box-elemento-" + data_['elemento']['codigo'] + "'>");
							$(elemento).append($('<h4 class="caps">').html(data_['elemento']['descripcion']));
							jQuery.each(data_['componentes'], function(index){
								$(elemento).append($("<div class='quiet'>").html(data_['componentes'][index][0] + data_['componentes'][index][1]));
							})
							$('#productos-compuestos').append(elemento);
							$('#productos-compuestos .box').hide();
							$(elemento).effect("highlight", {}, 3000);
						}
					}
				}
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				var inicio_sesion = XMLHttpRequest.getResponseHeader("inicio_sesion");
				if (eval(inicio_sesion))
				{
					top.location.href = '/venta/';
				}
				else
				{
					mensaje_error(XMLHttpRequest.responseText);
					$("input:text:visible").focus();					
				}
			}
		});
		return false;					
	});
	$("#a-ultima-venta").click(function(){
		/**
		 * Se maneja la interacci�n del evento click para mostrar
		 * la ultima venta registrada.
		 */
		pop_up($("#ultima-venta"),false,{'width':'700px','left':'22%'});
		return false;
	});	
	$("#ultima-venta").click(function(){
		$.unblockUI();
		$("input:text:visible").focus();
	})
	$("#a-cerrar-turno").click(function(){
		/**
		 * Evento que permite confirmar la acci�n del usuario
		 */
		if (confirm("Desea terminar el turno?")){
			return true;	
		}
		else{
			$("input:text:visible").focus();
			return false;
		}
	});
	$("#a-agregar").click(function(){
		/**
		 * Se maneja el env�o del formulario para que se 
		 * agrega la existencia al detalle de la venta.
		 */
		$("#formulario_detalle").submit();
		return false;
	});
	$("#a-cancelar").click(function(){
		/**
		 * Se maneja la interacci�n del evento click para cambiar
		 * de contenido el div actual, ya que el usuario ha cancelado
		 * la selecci�n del producto.
		 */		
		$('#codigo_barra').val('');
		$('#formulario_elemento').show();
		$('#formulario_detalle').hide();
		$('#codigo_barra').focus();
		return false;
	});
	$("#a-ayuda").click(function(){
		/**
		 * Se maneja la interacci�n del evento click para mostrar
		 * una breve ayuda al usuario.
		 */
		pop_up($("#ayuda"),false,{'width':'500px','left':'30%'});
		return false;
	});
	$("#ayuda").click(function(){
		$.unblockUI();
		$('#codigo_barra').focus();
	})
	$("#boton-calcular-vuelto").click(function(){
		/**
		 * Bot�n artificial para realizar venta utilizando el mouse.
		 */
		pop_up($("#vuelto"),false,{'width':'500px','left':'30%','margin-top':'-30px'});
		$("#vuelto-monto-total").html($("#monto-total").html());
		return false
		$.ajax({
			type: "GET",
			url: "/venta/ventana_vuelto/",
			cache: false,
			success: function(a_response){
				pop_up(a_response, false);
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				var inicio_sesion = XMLHttpRequest.getResponseHeader("inicio_sesion");
				if (eval(inicio_sesion))
				{
					top.location.href = '/venta/';
				}
				else
				{
					mensaje_error(XMLHttpRequest.responseText);
					$("input:text:visible").focus();					
				}
			}			
		});
		return false;
	});
	$("#vuelto-relleno-boton-cancelar-vuelto").click(function(){
		$.unblockUI();
		$('#codigo_barra').focus();
	})
	$("#vuelto-correcto-boton-cancelar-vuelto").click(function(){
		$.unblockUI();
		$('#codigo_barra').focus();		
	})
	$("#vuelto-incorrecto-boton-cancelar-vuelto").click(function(){
		$.unblockUI();
		$('#codigo_barra').focus();		
	})
	$("#boton-venta").click(function(){
		/**
		 * Bot�n artificial para realizar venta utilizando el mouse.
		 */
		if ($('#codigo_barra').val() == ""){
			generar_venta();
			return false;
		}
		return false;
	});	
	$(".medio_pago").change(function(){
		$("input:text:visible").focus();
		$.ajax({
			url: prefix + "/medio_pago/" + this.value + "/",
			cache: false,
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				var inicio_sesion = XMLHttpRequest.getResponseHeader("inicio_sesion");
				if (eval(inicio_sesion))
				{
					top.location.href = '/venta/';
				}
				else
				{
					mensaje_error(XMLHttpRequest.responseText);
					$("input:text:visible").focus();					
				}
			}
		});
	})
	$('#vuelto-pago-cliente').numeric();
	$('#vuelto-pago-cliente').keyup(calcular_vuelto);
	$('#vuelto-correcto-boton-venta').click(function(){
		$("#boton-venta").click();
	})
});
