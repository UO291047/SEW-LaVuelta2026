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

    getMeteorologia(){
        const apiKey = "dff06432f9d5b3e7c70f9a5f75d2615d";
        const url = "https://api.openweathermap.org/data/2.5/weather?lat=" + this.coords[1] + "&lon=" + this.coords[0] +
            "&mode=xml&units=metric&lang=es&appid=" + apiKey;

        $.ajax({
            dataType: "xml",
            url: url,
            method: "GET",
            success: (datos) => {
                this.procesarXML(datos);
                this.mostrarMeteorologia();
            },
            error: () => {
                $("main").append("<p>No se ha podido obtener la información meteorológica.</p>");
            }
        });
    }

    procesarXML(datos){
        this.meteorologia = {
            temperatura: $("temperature", datos).attr("value"),
            sensacionTermica: $("feels_like", datos).attr("value"),
            humedad: $("humidity", datos).attr("value"),
            presion: $("pressure", datos).attr("value"),
            velocidadViento: $("wind > speed", datos).attr("value"),
            direccionViento: $("wind > direction", datos).attr("value"),
            salidaSol: this.horaLocal($("city > sun", datos).attr("rise"), $("city > timezone", datos).text()),
            puestaSol: this.horaLocal($("city > sun", datos).attr("set"), $("city > timezone", datos).text()),
            icono: $("weather", datos).attr("icon"),
            descripcion: $("weather", datos).attr("value")
        };
    }

    horaLocal(horaUTC, desplazamiento){
        // OpenWeatherMap da las horas en UTC y el desplazamiento de la zona horaria en segundos
        const fecha = new Date(Date.parse(horaUTC + "Z") + Number(desplazamiento) * 1000);
        return String(fecha.getUTCHours()).padStart(2, "0") + ":" + String(fecha.getUTCMinutes()).padStart(2, "0");
    }

    mostrarMeteorologia(){
        const hoy = new Date();
        const fecha = String(hoy.getDate()).padStart(2, "0") + "/" + String(hoy.getMonth() + 1).padStart(2, "0") + "/" + hoy.getFullYear();

        const seccion = $("<section></section>");
        seccion.append($("<h3></h3>").text("El tiempo meteorológico hoy (" + fecha + ")"));
        seccion.append($("<img />")
            .attr("src", "https://openweathermap.org/img/wn/" + this.meteorologia.icono + "@2x.png")
            .attr("alt", this.meteorologia.descripcion)
            .attr("width", "100")
            .attr("height", "100"));

        const lista = $("<ul></ul>");
        lista.append($("<li></li>").text("Temperatura actual: " + this.meteorologia.temperatura + " ºC"));
        lista.append($("<li></li>").text("Sensación térmica: " + this.meteorologia.sensacionTermica + " ºC"));
        lista.append($("<li></li>").text("Humedad: " + this.meteorologia.humedad + " %"));
        lista.append($("<li></li>").text("Presión atmosférica: " + this.meteorologia.presion + " hPa"));
        lista.append($("<li></li>").text("Velocidad del viento: " + this.meteorologia.velocidadViento + " m/s"));
        lista.append($("<li></li>").text("Dirección del viento: " + this.meteorologia.direccionViento + "º"));
        lista.append($("<li></li>").text("Hora de salida del sol: " + this.meteorologia.salidaSol));
        lista.append($("<li></li>").text("Hora de puesta del sol: " + this.meteorologia.puestaSol));
        seccion.append(lista);

        $("main").append(seccion);
    }

}

let ciudad = new Ciudad("La Vila Joiosa/Villajoyosa", "España", "Viler");
ciudad.rellenarAtributos(37_449, [-0.213006, 38.538118]);

const seccion = document.createElement("section");

const titulo = document.createElement("h3");
titulo.textContent = ciudad.getCiudad() + " - " + ciudad.getPais();
seccion.appendChild(titulo);

seccion.insertAdjacentHTML("beforeEnd", ciudad.getInformacionSecundaria());

document.querySelector("h2").insertAdjacentElement("afterEnd", seccion);

ciudad.escribeCoordenadas();

ciudad.getMeteorologia();
