/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog�as Ltda. #
#                                             #
# �Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script contien todas las funcionas glables javascript necesaria
 para hacer funcionar venta.
  
 */

/**
 * prefijo, sufijo: utilizados para los mensajes que ser�n
 * mostrado al usuario dependiendo de sus acciones.
 */
var prefijo = '<h1 class="quiet">';
var sufijo = '</h1>';
var url_prefix = '/venta';

var mensaje_exito = function(a_mensaje){
	/**
	 * Mensaje generalmente utilizado para mostrar que una
	 * acción importante se llevá acabo (venta!).
	 */
	$.blockUI({message: prefijo + a_mensaje + sufijo, 
		css: { 
	        border: 'none', 
	        padding: '15px', 
	        backgroundColor: '#000', 
	        '-webkit-border-radius': '10px', 
	        '-moz-border-radius': '10px', 
	        opacity: .5, 
	        color: '#fff',
	    },
	    overlayCSS:  { 
	        backgroundColor: '#00BB00', 
	        opacity:         .5 
	    },			
	});
	setTimeout($.unblockUI, 2000);									
}

var mensaje_error = function(a_mensaje){
	/**
	 * Menseja generalmente utilizado para mostrar que una
	 * acci�n realizado por el usuario ha producido un error
	 * grave en la aplicaci�n (venta sin productos!).
	 */
	$.blockUI({message: prefijo + a_mensaje + sufijo, 
		css: { 
	        border: 'none', 
	        padding: '15px', 
	        backgroundColor: '#000', 
	        '-webkit-border-radius': '10px', 
	        '-moz-border-radius': '10px', 
	        opacity: .7, 
	        color: '#fff' 
	    	},
	    overlayCSS:  { 
	        backgroundColor: '#FF0000', 
	        opacity:         .5 
	    },			
	});
	setTimeout($.unblockUI, 2000);									
}

var mensaje_existencia_error = function(a_mensaje){
	/**
	 * Menseja generalmente utilizado para mostrar que una
	 * acci�n realizado por el usuario ha producido un error
	 * relacionado con existencia de productos o promociones.
	 */
	$.blockUI({message: prefijo + a_mensaje + sufijo, 
		css: { 
	        border: 'none', 
	        padding: '15px', 
	        backgroundColor: '#000', 
	        '-webkit-border-radius': '10px', 
	        '-moz-border-radius': '10px', 
	        opacity: .7, 
	        color: '#fff',
	        width:'600px',
	        left:'23%',
	        top:'30%'
	    	},
	    overlayCSS:  { 
	        backgroundColor: '#000099', 
	        opacity:         .5 
	    },			
	});
	$(this).click(function(){
		$.unblockUI();
		$("input:text:visible").focus();
	})
}

var mensaje_turno_abierto = function(a_mensaje){
	/**
	 * Menseja generalmente utilizado para mostrar que una
	 * acci�n realizado por el usuario ha producido un error
	 * grave en la aplicaci�n (venta sin productos!).
	 */
	$.blockUI({message: prefijo + a_mensaje + sufijo, 
		css: { 
	        border: 'none', 
	        padding: '15px', 
	        backgroundColor: '#000', 
	        '-webkit-border-radius': '10px', 
	        '-moz-border-radius': '10px', 
	        opacity: .7, 
	        color: '#fff' 
	    	},
	    overlayCSS:  { 
	        backgroundColor: '#FF0000', 
	        opacity:         .5 
	    },			
	});			
}

var generar_venta = function(){
	/**
	 * Funci�n global que realiza la tarea dura de realizar
	 * la venta.
	 */
	if (confirm('Desea registrar la venta?')){
		$.ajax({
			url: url_prefix + "/registrar/",
			cache: false,
			dataType: 'json',
			success: function(data_){
				modificar_datos_venta(data_['venta']);
				modificar_datos_cabecera_venta(data_['venta']);
				modificar_datos_ultima_venta(data_['ultima_venta']);
				$('#productos-compuestos .box-elemento').remove();
				$('#promociones .box-elemento').remove();
				$('#productos-compuestos .box').show();				
				$('#promociones .box').show()
				$('#boton-calcular-vuelto').hide();
				$('#elementos-venta tbody tr').remove();
				$('#elementos-venta').hide();
				$('#detalle-vacio').show();
				$('#codigo_barra').focus();
				$('#medio-pago-efectivo').attr('checked',true);
				mensaje_exito("Venta ha sido registrada de forma exitosa");
				$("#vuelto-pago-cliente").bind('keyup',calcular_vuelto);				
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
	}
	else{
		/**
		 * Se vincula nuevamente la funcion al evento keyup del calculador
		 * de vuelto.
		 */
		$("#vuelto-pago-cliente").bind('keyup',calcular_vuelto);
	}
};

/**
 * Se declara funcion global, para poder hacerla funcionar
 * desde varios document.ready.  De seguro existe una mejor
 * forma de hacer esto, pero es la unica forma que se encontr�.
 * @param {Object} e
 */
var calcular_vuelto = function(e){
	/**
	 * Se maneja los cambios a partir de las teclas levantadas del usuario,
	 * dependiendo de estas se realiza una llamada as�ncrona y se calcula
	 * el vuelto que se le debe entregar al cliente.
	 */
	if (isNaN(parseInt($(this).val())) == true) {
		return false;
	}
	$(this).val(parseInt($(this).val()));	
	if (e.keyCode == 13){
		$("#vuelto-pago-cliente").unbind('keyup',calcular_vuelto);
		$("#boton-venta").click();
		return false;			
	}
	$.ajax({ 
        url: url_prefix + '/vuelto/' + $(this).val() + '/' , 
        cache: false,
		dataType: 'json',
       	success: function(data_) {
			if (data_['cantidad_correcta']){
				$("#vuelto-correcto").show();
				$("#vuelto-incorrecto").hide();
				$("#vuelto-relleno").hide();
				$("#vuelto-correcto-monto-vuelto").html(data_['total_vuelto']);
			}
			else{
				$("#vuelto-relleno").hide();
				$("#vuelto-incorrecto-monto-vuelto").html(data_['total_vuelto']);				
				$("#vuelto-incorrecto").show();				
				$("#vuelto-correcto").hide();				
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
};

var pop_up = function(a_contenido, a_timeout, a_opciones, a_tiempo){
	/**
	 * Ventana utilizada para que el usuario interact�e
	 * de alguna forma con la interfaz de usuario.
	 * Esta ventana simular un pop_up pero realmente
	 * s�lo es un div con contenido.
	 */
	var css = {
        border: 'none', 
        padding: '15px', 
        backgroundColor: '#000', 
        '-webkit-border-radius': '10px', 
        '-moz-border-radius': '10px', 
        opacity: .7, 
        color: '#fff',
		top:'30%'		
	}
	$.extend(css, a_opciones)
	$.blockUI({
		message: a_contenido,
		css:css,
	    overlayCSS:  { 
	        backgroundColor: '#DDDDFF', 
	        opacity:.5 
	    },			
	});
	if (a_timeout){
		setTimeout($.unblockUI, a_tiempo);											
	}
}

var generar_devolucion = function(){
	/**
	 * Funci�n global que realiza la tarea dura de realizar
	 * la devolucion.
	 */
	if (confirm('Desea registrar la devolucion?')){
		var campos_formulario = $('#formulario_detalle :text').fieldSerialize();
		$.ajax({
			type: "POST",
			url: "/venta/devolucion/cuerpo_devolucion/",
			data: campos_formulario,
			cache: false,
			success: function(a_response){
				mensaje_exito("Devolucion ha sido registrada de forma exitosa");
				setTimeout(function(){
					top.location.href = '/venta/venta/'
				},2000);
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
	}
};

var aumentar = function(){
	/**
	 * Evento utilizado para que el usuario pueda aumentar
	 * un elemento del detalle de la venta.
	 */
	var fila = $(this).parents('tbody tr');
	var cantidad = fila.find(".cantidad");
	var precio_total = fila.find(".precio_total");
	var url = String(this);
	$.ajax({
		url: url,
		cache: false,
		dataType: 'json',
		success: function(data_){
			fila.effect("highlight", {}, 500);
			cantidad.html(data_['elemento']['cantidad']);
			precio_total.html(data_['elemento']['precio_total']);
			if (cantidadToInt(data_['elemento']['cantidad']) > 1){
				fila.find(".a-disminuir").show();
			}
			modificar_datos_venta(data_['venta'])
			$("input:text:visible").focus();		
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
};

var disminuir = function(){
	/**
	 * Evento utilizado para que el usuario pueda disminuir
	 * un elemento del detalle de la venta.
	 */
	var fila = $(this).parents('tbody tr');
	var cantidad = fila.find(".cantidad");
	var precio_total = fila.find(".precio_total");
	var url = String(this);
	$.ajax({
		url: url,
		cache: false,
		dataType: 'json',
		success: function(data_){
			fila.effect("highlight", {}, 500);
			cantidad.html(data_['elemento']['cantidad']);
			precio_total.html(data_['elemento']['precio_total']); //poner formateador de pesos
			if (cantidadToInt(data_['elemento']['cantidad']) == 1){
				fila.find(".a-disminuir").hide();
			}
			modificar_datos_venta(data_['venta'])
			$("input:text:visible").focus();
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
};

var eliminar = function(){
	/**
	 * Evento utilizado para que el usuario puede eliminar 
	 * un elemento del detalle de la venta.
	 */
	if (confirm("Desea eliminar este elemento del detalle de venta?"))
	{  
		var fila = $(this).parents('tbody tr');
		var id = $(fila).attr('id').split('-')[2];
		$.ajax({
			url: String(this),
			cache: false,
			dataType: 'json',
			success: function(data_){
				modificar_datos_venta(data_['venta']);
				$("#box-elemento-" + id).remove();				
				if ($("#promociones .box-elemento").length == 0){
					$("#promociones .box").show();				
				}
				if ($("#productos-compuestos .box-elemento").length == 0){
					$("#productos-compuestos .box").show();				
				}
				eliminar_fila(fila);
				$("input:text:visible").focus();
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
	}
	else{
		$("input:text:visible").focus();
	}
	return false;
}

var modificar_datos_venta = function(data_){
	$('#total_afecto').html(data_['total_afecto']);			
	$('#total_exento').html(data_['total_exento']);			
	$('#total-productos').html(data_['total_productos']);			
	$('#monto-total').html(data_['monto_total']);			
}

var modificar_datos_cabecera_turno = function(data_){
	$('#turno-trabajador').html(data_['trabajador']);			
	$('#turno-sucursal').html(data_['sucursal']);			
	$('#turno-fecha-apertura-sistema').html(data_['fecha_apertura_sistema']);
}

var modificar_datos_cabecera_venta = function(data_){
	$('#venta-fecha-venta').html(data_['fecha_venta']);
}

var construir_fila = function(data_, indice_){
	var clase = 'impar';
	if (indice_%2==0) clase = '';
	var fila = $('<tr id="elementos-venta-' + data_["elemento"]["codigo"] +'" class="'+ clase +'">');
	var enlace = $('<a>');
	var columna = $('<td>'); 
	$(enlace).attr('href',"/venta/elemento/delete/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-eliminar');
	$(enlace).attr('title','Eliminar');
	$(enlace).click(eliminar);				
	$(columna).append($(enlace));
	enlace = $('<a>');
	$(enlace).attr('href',"/venta/elemento/aumentar/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-aumentar');
	$(enlace).attr('title','Aumentar');
	$(enlace).click(aumentar);				
	$(columna).append($(enlace));
	enlace = $('<a>');
	$(enlace).attr('href',"/venta/elemento/disminuir/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-disminuir');
	$(enlace).attr('title','Disminuir');
	if (data_['elemento']['cantidad'] == 1){
		$(enlace).attr('style','display:none');
	}
	$(enlace).click(disminuir);				
	$(columna).append($(enlace));				
	$(fila).append($(columna));
	$(fila).append($('<td>').append(data_['elemento']['descripcion']));
	$(fila).append($('<td>').append(data_['elemento']['precio_venta']));
	$(fila).append($('<td>').append($("<span class='cantidad'>").append(data_['elemento']['cantidad'])));
	$(fila).append($('<td>').append($("<span class='precio_total'>").append(data_['elemento']['precio_total'])));				
	return fila;	
}

var eliminar_fila = function(fila_){
	var tabla = $(fila_).parents('table');
	var filas = $('#elementos-venta tbody tr');
	var cantidad_filas = $(filas).length
	if (cantidad_filas == 1){
		tabla.hide();
		$('#boton-calcular-vuelto').hide();
		$('#detalle-vacio').show();	
	}
	fila_.remove();
}

var monedaToInt = function(valor_){
	valor_ = valor_.toString();
	valor_ = valor_.replace('CLP$','');
	valor_ = valor_.replace('.','');
	valor_ = valor_.replace('-','');	
	return parseInt(valor_);
}

var cantidadToInt = function(valor_){
	valor_ = valor_.toString();
	valor_ = valor_.replace('.','');
	return parseInt(valor_);
}

var modificar_datos_ultima_venta = function(data_){
	$('#elementos-ultima-venta tbody tr').remove();
	$('#elementos-ultima-venta tfoot tr').remove();		
	var pie = construir_pie_ultima_venta(data_);
	jQuery.each(data_['elementos'],function(index,elemento){
		fila = construir_fila_ultima_venta(elemento);
		$('#elementos-ultima-venta tbody').append(fila);
	});
	$('#elementos-ultima-venta tfoot').append(pie);
	$('#a-ultima-venta').show();
	$('#tabla-resumen-ultima-venta-span').hide();
}

var construir_fila_ultima_venta = function(data_){
	var fila = $('<tr>');
	$(fila).append($('<td>').append(data_['descripcion']));
	$(fila).append($('<td>').append(data_['precio_venta']));	
	$(fila).append($('<td>').append($("<span class='cantidad'>").append(data_['cantidad'])));
	$(fila).append($('<td>').append($("<span class='precio_total'>").append(data_['precio_total'])));				
	return fila;	
}

var construir_pie_ultima_venta = function(data_){
	var fila = $('<tr>');
	$(fila).append($('<td>'));
	$(fila).append($('<td>').append('TOTALES'));	
	$(fila).append($('<td class="linea">').append($("<span class='cantidad'>").append(data_['cantidad'])));
	$(fila).append($('<td class="linea">').append($("<span class='precio_total'>").append(data_['monto_total'])));				
	return fila;	
}

