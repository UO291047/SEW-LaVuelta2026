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
                tagmode: "all",
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

            const titulo = item.title !== "" ? item.title : "Fotografía de La Vuelta 2026";

            this.fotografias.push({ url: url, titulo: titulo });

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

        setInterval(this.cambiarFotografia.bind(this), 3000);
    }

    cambiarFotografia(){
        this.actual++;
        if (this.actual > this.maximo || this.actual >= this.fotografias.length) {
            this.actual = 0;
        }

        const foto = this.fotografias[this.actual];
        $("main > article > img").attr("src", foto.url).attr("alt", foto.titulo);
    }

}
