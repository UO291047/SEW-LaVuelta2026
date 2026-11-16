"use strict";

class Noticias{

    constructor(busqueda){
        this.busqueda = busqueda;
        this.url = "https://api.thenewsapi.com/v1/news/all?api_token=3UCUUZENe0dc2LjQceHGL8U32oCyKYr2PxTNZR7N";
        this.noticias = [];
    }

    buscar(){
        return fetch(this.url + "&search=" + encodeURIComponent(this.busqueda))
            .then(respuesta => {
                if (!respuesta.ok) {
                    throw new Error("Error en la respuesta del servicio de noticias: " + respuesta.status);
                }
                return respuesta.json();
            });
    }

    procesarInformacion(datos){
        this.noticias = [];
        datos.data.forEach(noticia => {
            this.noticias.push({
                titular: noticia.title,
                entradilla: noticia.description,
                enlace: noticia.url,
                fuente: noticia.source
            });
        });
    }

    mostrarNoticias(){
        const seccion = $("<section></section>");
        seccion.append($("<h3></h3>").text("Noticias"));

        if (this.noticias.length === 0) {
            seccion.append($("<p></p>").text("No se han encontrado noticias."));
        }

        this.noticias.forEach(noticia => {
            const articulo = $("<article></article>");
            articulo.append($("<h4></h4>").text(noticia.titular));
            articulo.append($("<p></p>").text(noticia.entradilla));
            articulo.append($("<p></p>").append($("<a></a>").attr("href", noticia.enlace).text("Leer la noticia en " + noticia.fuente)));
            seccion.append(articulo);
        });

        $("main").append(seccion);
    }

}

const noticias = new Noticias("Tudor + Vuelta");
noticias.buscar()
    .then(datos => {
        noticias.procesarInformacion(datos);
        noticias.mostrarNoticias();
    })
    .catch(error => {
        $("main").append($("<p></p>").text("No se han podido obtener las noticias: " + error.message));
    });
