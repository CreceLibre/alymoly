/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnologías Ltda. #
#                                             #
# Andrés Otárola Alvarado                     #
# andres@otarola.me                           #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

 El siguiente script realiza una llamada ajax para recargar el nombre de un producto,
 dado su código de barra

 * */

$(document).ready(function() {

  var reset_campo = function(obj) {

    obj.siblings('.codigo_barra').show().css({
      "border": ""
    }).focus();
    obj.siblings('._detalle').remove();
    obj.remove();
  }

  var info_producto = function(obj) {

    if (obj.val() != '')
      $.ajax({
        url: "/admin/utils/producto/nombre/",
        type: 'GET',
        data: "codigo_barra=" + obj.val(),
        success: function(html) {
          resp = eval(html);
          if (!resp[1]) resp[1] = ""
          obj.after('<span class="nombre_producto" style="font-size:2em">' + resp[0] + '</span><p class="_detalle" style="color: blue; font-weight: bolder;">' + resp[1] + '</p>').hide()
          obj.siblings('.nombre_producto').click(function() {

            reset_campo($(this));

          })
        },
        error: function(html) {
          errores = JSON.parse(html.responseText)
          obj.css({
            "border": "1px solid red"
          });
          alert(errores['codigo_barra'])
        }
      });

  }

  $('.codigo_barra').blur(
    function() {
      info_producto($(this));
    }
  );


  $('.codigo_barra').each(function() {
    var obj = $(this);
    if (obj.val() != '')
      obj.blur();
  })

});
