/**
# # # # # # # # # # # # # # # # # # # # # # # #
# Todos los derechos reservados a:            #
# CreceLibre Consultores en Tecnolog�as Ltda. #
#                                             #
# �Andr�s Ot�rola Alvarado                    #
# aotarola@crecelibre.cl                      #
# 2009                                        #
# # # # # # # # # # # # # # # # # # # # # # # #

 El siguiente script recarga el combobox de subcategor�a, dependiendo
 de la categor�a seleccionada
 * */

$(document).ready(function() {

    var categoria = $('select#id_categoria')
    var subcategoria = $('select#id_subcategoria')

    var splitted_url = new String(window.location).split("/")

    var product_id = splitted_url[splitted_url.length - 2]

    subcategoria.empty()

    var actualizarSubcategoria = function(e) {

      var categoria_id = $('select#id_categoria').val()

      if (categoria_id) {

        $.getJSON("/admin/subcategorias/" + categoria_id + "/",
          function(data) {
            if (data.length > 0) {
              var myOptions = {
                "": "Ninguna",
              }
              $.each(myOptions, function(val, text) {

                subcategoria.append($('<option>').val(val).html(text))

              });
              $.each(data, function(i, item) {
                var nombre = $.cap(item.fields.nombre)
                if (e == item.pk) {
                  subcategoria.append($('<option>').val(item.pk).attr("selected", "selected").html(nombre))
                } else {
                  subcategoria.append($('<option>').val(item.pk).html(nombre))
                }

              });
            } else {
              var myOptions = {
                "": "No hay subcategor&iacute;as asociadas",
              }
              $.each(myOptions, function(val, text) {

                subcategoria.append($('<option>').val(val).html(text))

              });
            }

          });
      } else {

        var myOptions = {
          "": "Seleccione una categor&iacute;a primero",
        }
        $.each(myOptions, function(val, text) {

          subcategoria.append($('<option>').val(val).html(text))

        });
      }


    }

    if (product_id != 'add') {
      $.getJSON("/admin/subcategoria_de_producto/" + "1764",
        function(data) {
          categoria.val(data.supercategoria)
          if (data.subcategoria) {

            actualizarSubcategoria(data.subcategoria);
          } else {

            actualizarSubcategoria(null);
          }
        });
    } else {

      actualizarSubcategoria();
    }

    $('select#id_categoria').change(function() {

      subcategoria.empty();
      actualizarSubcategoria();
    })

  }

);
