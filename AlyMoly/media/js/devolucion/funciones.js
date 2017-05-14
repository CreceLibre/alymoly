/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog’as Ltda. #
#                                             #
# ©Milton Inostroza Aguilera                  #
# minostro@minostro.com                       #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script contien todas las funcionas glables javascript necesaria
 para hacer funcionar venta.
  
 */

/**
 * prefijo, sufijo: utilizados para los mensajes que ser‡n
 * mostrado al usuario dependiendo de sus acciones.
 */
var prefijo = '<h1 class="quiet">';
var sufijo = '</h1>';
var url_prefix = '/devolucion';

var mensaje_exito = function(a_mensaje){
	/**
	 * Mensaje generalmente utilizado para mostrar que una
	 * acci—n importante se llev— acabo (venta!).
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
	 * acci—n realizado por el usuario ha producido un error
	 * grave en la aplicaci—n (venta sin productos!).
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

var pop_up = function(a_contenido, a_timeout, a_opciones, a_tiempo){
	/**
	 * Ventana utilizada para que el usuario interactœe
	 * de alguna forma con la interfaz de usuario.
	 * Esta ventana simular un pop_up pero realmente
	 * s—lo es un div con contenido.
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
	 * Funci—n global que realiza la tarea dura de realizar
	 * la devolucion.
	 */
	if (confirm('Desea registrar la devolucion?')){
		$.ajax({
			url: url_prefix + "/registrar/",
			cache: false,
			success: function(a_response){
				mensaje_exito("Devolucion ha sido registrada de forma exitosa");
				setTimeout(function(){
					top.location.href = '/venta/venta/'
				},2000);
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				mensaje_error(XMLHttpRequest.responseText);
				$("input:text:visible").focus();
			}
		});
	}
	else{
		$('boton-devolucion').focus();
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
			$("#boton-devolucion").focus();
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			mensaje_error(XMLHttpRequest.responseText);
			$("input:text:visible").focus();
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
			$("#boton-devolucion").focus();
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			mensaje_error(XMLHttpRequest.responseText);
			$("input:text:visible").focus();
		}
	});
	return false;
};

var eliminar = function(){
	/**
	 * Evento utilizado para que el usuario puede eliminar 
	 * un elemento del detalle de la venta.
	 */
	if (confirm("Desea eliminar este elemento del detalle de devolucion?"))
	{  
		$.ajax({
			url: String(this),
			cache: false,
			success: function(a_response){
				interfas_inicial();
			},
			error: function (XMLHttpRequest, textStatus, errorThrown) {
				mensaje_error(XMLHttpRequest.responseText);
				$("input:text:visible").focus();
			}
		});			
	}
	else{
		$("#boton-devolucion").focus();
	}
	return false;
}

var interfas_inicial = function(){
	$('#elementos-devolucion tbody tr').remove();
	$('#detalle-devolucion').hide();
	$('#formulario-detalle').hide();
	$('#buscador-detalle').show();
	$('#formulario-elemento').show();
	$("input:text:visible").focus();	
}

var modificar_datos_cabecera_turno = function(data_){
	$('#turno-trabajador').html(data_['trabajador']);			
	$('#turno-sucursal').html(data_['sucursal']);			
	$('#turno-fecha-apertura-sistema').html(data_['fecha_apertura_sistema']);
}

var modificar_datos_cabecera_venta = function(data_){
	$('#venta-fecha-venta').html(data_['fecha_venta']);
}

var construir_fila = function(data_){
	var fila = $('<tr id="elementos-venta-' + data_["elemento"]["codigo"] +'">');
	var enlace = $('<a>');
	var columna = $('<div id="elementos-venta-opciones">');
	$(enlace).attr('href',url_prefix + "/elemento/delete/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-eliminar');
	$(enlace).attr('title','Eliminar');
	$(enlace).click(eliminar);				
	$(columna).append($(enlace));
	enlace = $('<a>');
	$(enlace).attr('href',url_prefix + "/elemento/aumentar/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-aumentar');
	$(enlace).attr('title','Aumentar');
	$(enlace).click(aumentar);				
	$(columna).append($(enlace));
	enlace = $('<a>');
	$(enlace).attr('href',url_prefix + "/elemento/disminuir/" + data_["elemento"]["codigo"] + "/");
	$(enlace).attr('class','a-disminuir');
	$(enlace).attr('title','Disminuir');
	if (data_['elemento']['cantidad'] == 1){
		$(enlace).attr('style','display:none');
	}
	$(enlace).click(disminuir);				
	$(columna).append($(enlace));				
	$(fila).append($('<td>').append(columna));
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
