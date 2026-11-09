"use strict";

class Buscador{

    constructor(){
        document.querySelector("search label img").addEventListener("click", this.buscar.bind(this));

        document.querySelector("search input").addEventListener("keypress", function(evento){
            if (evento.key === "Enter") {
                this.buscar();
            }
        }.bind(this));
    }

    buscar(){
        this.limpiar_busqueda();

        const resultados = [];
        const texto = document.querySelector("search input").value;

        if (texto !== "") {
            const regexp = new RegExp(texto, "gi");
            const nodos = document.createTreeWalker(document.querySelector("body"), NodeFilter.SHOW_TEXT);

            let nodo = nodos.nextNode();
            while (nodo !== null) {
                regexp.lastIndex = 0; // con el parámetro 'g', test() continúa desde la posición de la última coincidencia
                if (regexp.test(nodo.textContent)) {
                    resultados.push(nodo);
                }
                nodo = nodos.nextNode();
            }

            resultados.forEach(nodo => {
                const nuevoTexto = nodo.textContent.replaceAll(regexp, "<mark>$&</mark>");
                nodo.parentElement.innerHTML = nuevoTexto;
            });
        }
    }

    limpiar_busqueda(){
        document.querySelectorAll("mark").forEach(marca => {
            marca.replaceWith(document.createTextNode(marca.textContent));
        });
        document.body.normalize();
    }

}

const buscador = new Buscador();
