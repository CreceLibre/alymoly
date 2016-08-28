/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# ©Andrés Otárola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

 El siguiente script realiza una llamada ajax para recargar el nombre de un producto,
 dado su código de barra

 * */

$(document).ready(function(){

	var reset_campo = function(obj){

		obj.siblings('.codigo_barra_busqueda').show().css({"border":""}).focus();
		$('.related-lookup').show();
		obj.siblings('._detalle').remove();
		obj.remove();
	}

	var info_producto = function(obj){
		if(obj.val() != '')
        $.ajax({
     	   url: "/admin/utils/producto/nombre/",
     	   type: 'GET',
     	   data: "codigo_barra="+obj.val(),
     	   success: function(html){
        		resp = eval(html);
        		if(!resp[1]) resp[1] = ""
        		obj.after('<span class="nombre_producto" style="font-size:2em">'+resp[0]+'</span><p class="_detalle" style="color: blue; font-weight: bolder;">'+resp[1]+'</p>').hide()
        		$('.related-lookup').hide();
        		obj.siblings('.nombre_producto').click(function(){

        			reset_campo($(this));

        		})
        	},
          error: function(html){
        		errores = JSON.parse(html.responseText)
        		obj.css({"border":"1px solid red"});
        		obj.val('')
        	}
     	 });

	}

	$('.codigo_barra_busqueda').after('<a  id="lookup_id" class="related-lookup" href="../../../producto/?es_compuesto__exact=0">'+
			'<img height="16" width="16" alt="Buscar" src="/media/img/selector-search.gif">'+'</a>')

			dismissRelatedLookupPopup = function(win, chosenId) {
	       $.ajax({
	    	   url: "/admin/utils/producto/detalle/"+chosenId+"/",
	    	   cache: false,
	    	   dataType: "json",
	    	   success: function(html){
	    	   	$('#id_compuesto_por').val(html['codigo_barra']);
	    	   	info_producto($('.codigo_barra_busqueda'));
	    	   }
	    	 });
			win.close();
			}

	$('#lookup_id').click(function(){
		if($('.codigo_barra_busqueda').val() != ''){
			info_producto($('.codigo_barra_busqueda'));
			return false;
		}
		else{
			return showRelatedObjectLookupPopup(this);
		}
	})


	$('.codigo_barra_busqueda').live('keypress', function (e) {
		   if ( e.keyCode == 9 ){
			   info_producto($('.codigo_barra_busqueda'));
		    }
		});

	if($('.codigo_barra_busqueda').val() != '')
		info_producto($('.codigo_barra_busqueda'));
});
