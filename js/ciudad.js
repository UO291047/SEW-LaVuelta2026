"use strict";
class Ciudad{

    constructor(nombreCiudad, pais, gentilicio){
        this.nombreCiudad = nombreCiudad;
        this.pais = pais;
        this.gentilicio = gentilicio;
    }

    rellenarAtributos(poblacion, coords){
        this.poblacion = poblacion;
        this.coords = coords;
    }

    getCiudad(){
        return this.nombreCiudad;
    }

    getPais(){
        return this.pais;
    }

    getInformacionSecundaria(){
        return "<ul>" +
                    "<li>Gentilicio: " + this.gentilicio + "</li>" +
                    "<li>Población: " + this.poblacion + "</li>" +
                "</ul>";
    }

    escribeCoordenadas(){
        document.querySelector("section").insertAdjacentHTML("beforeend", "<p>" + "Coordenadas: [" + this.coords + "]" + "</p>");
    }

}

let ciudad = new Ciudad("La Vila Joiosa/ Villajoyosa", "España", "Viler");
ciudad.rellenarAtributos(37_449, [-0.213006, 38.538118]);

const seccion = document.createElement("section");

const titulo = document.createElement("h3");
titulo.textContent = ciudad.getCiudad() + " - " + ciudad.getPais();
seccion.appendChild(titulo);

seccion.insertAdjacentHTML("beforeEnd", ciudad.getInformacionSecundaria());

document.querySelector("h2").insertAdjacentElement("afterEnd", seccion);

ciudad.escribeCoordenadas();