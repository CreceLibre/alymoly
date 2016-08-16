/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #
  
 El siguiente script recarga vía ajax el stock actual, cuando es seleccionada una bodega
  
 */
var actualiza_existencias = function(){
	$(".valor_existencia").numeric()
	$(".valor_existencia").change(function(){
		var existencia = $(this)
		temp = new String(this.id)
		id_producto_bodega = temp.substring(temp.indexOf('-')+1,temp.length)
		if(confirm('A continuacion se establecera el valor de existencia "'+$(this).val() + '" para el producto seleccionado. Desea continuar?.')){
		my_element = $(this)
		if(existencia.val() == ''){
			existencia.val(0)
		}
        $.ajax({
    	   url: "/admin/inventario/existencia/actualizar/",
    	   type: "POST",
    	   data: "producto_bodega="+id_producto_bodega+"&existencia="+existencia.val(),
    	   success: function(html){
        	my_element.parents('tr').effect("highlight", {}, 3000);
        	},
           error: function(html){
        	my_element.parents('tr').effect("highlight", {color:'#FA5858'}, 3000);
        	//errores = JSON.parse(html.responseText)
        	//console.log(errores['__all__'])
        	alert('Ha ocurrido un error al actualizar la existencia.')
        	}
    	 });
		}
		
	})
}
var cargar_productos = function(){
		
		
		if($('#id_texto').val()!= ''){
			buscar_productos();
		}
		else{
		bodega = $('select#id_bodega');
		$.blockUI({ 			message: "<h1>Cargando productos...</h1>", css: { 

            border: 'none', 
            padding: '15px', 
            backgroundColor: '#000', 
            '-webkit-border-radius': '10px', 
            '-moz-border-radius': '10px', 
            opacity: .5, 
            color: '#fff' 
        } });
	       $.ajax({
	    	   url: "/admin/inventario/actual/"+bodega.val()+"/",
	    	   success: function(html){
	    	   $('#inventario-actual').html(html)
	    	   $.unblockUI();
	    	   actualiza_existencias();
	    	   },
	       	error: function (XMLHttpRequest, textStatus, errorThrown) {
	    		   $.unblockUI();
	    		 }

	    	 });
		}
	}

$(document).ready(function(){
	
	$('select#id_bodega').change(function(e){
		if($('select#id_bodega').val() == '')
			$('#inventario-actual').html('')
		else
			cargar_productos();
		
		}
	 )
	 
	 if($('select#id_bodega').val() != ''){cargar_productos();}
})
