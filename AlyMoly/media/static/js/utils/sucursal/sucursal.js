$(document).ready(function(){
	$.ajax({
		url: '/admin/utils/sucursal/',
		cache: false,
		dataType: 'json',
		success: function(data_){
			$('#nombre-sucursal').text(data_['nombre_sucursal'])		
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			$('#nombre-sucursal').text('-')
		}
	});				
})
