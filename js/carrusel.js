"use strict";

class Carrusel{

    constructor(busqueda){
        this.busqueda = busqueda;
        this.actual = 0;
        this.maximo = 4;
        this.fotografias = [];
    }

    getFotografias(){
        const flickrAPI = "https://api.flickr.com/services/feeds/photos_public.gne?jsoncallback=?";
        $.getJSON(flickrAPI,
            {
                tags: this.busqueda,
                tagmode: "any",
                format: "json"
            })
            .done((datos) => {
                this.procesarJSONFotografias(datos);
                this.mostrarFotografias();
            });
    }

    procesarJSONFotografias(datos){
        this.fotografias = [];
        $.each(datos.items, (i, item) => {
            const url = item.media.m.replace("_m.", "_z.");

            this.fotografias.push({ url: url, titulo: item.title });

            return this.fotografias.length <= this.maximo;
        });
    }

    mostrarFotografias(){
        if (this.fotografias.length === 0) {
            return;
        }

        const articulo = $("<article></article>");
        articulo.append($("<h2></h2>").text("Instantáneas de LaVuelta"));

        const foto = this.fotografias[this.actual];
        articulo.append($("<img />").attr("src", foto.url).attr("alt", foto.titulo));

        $("main > h2").after(articulo);

        setInterval(() => {
            this.cambiarFotografia();
        }, 3000);
    }

    cambiarFotografia(){
        this.actual = (this.actual + 1) % this.fotografias.length;
        const foto = this.fotografias[this.actual];
        $("main > article > img").attr("src", foto.url).attr("alt", foto.titulo);
    }

}

const carrusel = new Carrusel("lavuelta2026, lavueltaciclista");
carrusel.getFotografias();
