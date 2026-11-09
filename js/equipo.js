"use strict";

class Ciclista{
    constructor(nombre, apellidos, dorsal, fechaNacimiento, nacionalidad){
        this.nombre = nombre;
        this.apellidos = apellidos;
        this.dorsal = dorsal;
        this.fechaNacimiento = fechaNacimiento;
        this.nacionalidad = nacionalidad;
    }

    getNombreCompleto(){
        return this.nombre + " - " + this.apellidos;
    }

    getDorsal(){
        return this.dorsal;
    }

    getInformacionAdicional(){
        return this.fechaNacimiento + ", " + this.nacionalidad;
    }
}

class Equipo{

    constructor(nombre, codigoUCI, pais){
        this.nombre = nombre;
        this.codigoUCI = codigoUCI;
        this.pais = pais;
        this.alineacion = [];
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

    async leerEquipo(){
        try {
            const respuesta = await fetch("js/lavuelta.json");
            if (!respuesta.ok) throw new Error('Archivo no encontrado');
            const datos = await respuesta.json();
            const equipo = datos.equipos.find(e => e.codigo_uci === this.codigoUCI);

            this.alinearCiclistas(equipo);
        } catch (error) {
            this.resultado.textContent = 'Error al obtener los equipos: ' + error.message;
        }            
    }

    alinearCiclistas(equipo){
        equipo.corredores.forEach(ciclista => {
            const nuevoCiclista = new Ciclista(ciclista.nombre, ciclista.apellidos, ciclista.dorsal, ciclista.fecha_nacimiento, ciclista.nacionalidad);
            this.alineacion.push(nuevoCiclista);
        });
    }

    mostrarAlineacion(){
        const seccion = document.createElement("section");
        const titulo = document.createElement("h3");
        titulo.textContent = "Alineación de corredores";
        seccion.appendChild(titulo);

        this.alineacion.sort((ciclistaA, ciclistaB) => ciclistaA.getDorsal() - ciclistaB.getDorsal());

        this.alineacion.forEach(ciclista => {
            const articulo = document.createElement("article");
            const nombreCompleto = document.createElement("h4");
            nombreCompleto.textContent = ciclista.getNombreCompleto();
            articulo.appendChild(nombreCompleto);
            
            articulo.insertAdjacentHTML("beforeend", "<img src=\"multimedia/ciclistaGenerico.png\" alt=\"Icono de un ciclista genérico\" width=\"128\" height=\"128\" />");

            const dorsal = document.createElement("p");
            dorsal.textContent = "Dorsal: " + ciclista.getDorsal();
            articulo.appendChild(dorsal);

            const informacionAdicional = document.createElement("p");
            informacionAdicional.textContent = ciclista.getInformacionAdicional();
            articulo.appendChild(informacionAdicional);

            seccion.appendChild(articulo);
        });

        document.querySelector("section").insertAdjacentElement("afterend", seccion);
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

equipo.leerEquipo().then(() => {
    equipo.mostrarAlineacion();
});