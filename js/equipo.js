"use strict";
class Equipo{

    constructor(nombre, codigoUCI, pais){
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
    }

    rellenarAtributos(director, categoria, paginaWeb){
        this.director = director;
        this.categoria = categoria;
        this.paginaWeb = paginaWeb;
    }

    datosBasicos(){
        return this.nombre + " (" + this.codigoUCI + ")";
    }

    getPais(){
        return this.pais;
    }

    getInformacionSecundaria(){
        return "<ul>" +
                    "<li>Director: " + this.director + "</li>" +
                    "<li>Categoría: " + this.categoria + "</li>" +
                "</ul>";
    }

    getPaginaWeb(){
        document.querySelector("section").insertAdjacentHTML("beforeend", "<p>" + "Ficha del equipo en La Vuelta: " + "<a href=\"" + this.paginaWeb + "\">" + this.paginaWeb + "</a>" + "</p>");
    }

}

let equipo = new Equipo("Tudor Pro Cycling Team", "TUD", "Suiza");
equipo.rellenarAtributos("Bart Leysen", "UCI ProTeam", "https://www.lavuelta.es/es/equipo/TUD/tudor-pro-cycling-team");

const seccion = document.createElement("section");

const titulo = document.createElement("h3");
titulo.textContent = equipo.datosBasicos() + " - " + equipo.getPais();
seccion.appendChild(titulo);

seccion.insertAdjacentHTML("beforeend", equipo.getInformacionSecundaria());

document.querySelector("h2").insertAdjacentElement("afterend", seccion);

equipo.getPaginaWeb();
