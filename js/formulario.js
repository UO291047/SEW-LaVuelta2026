"use strict";

class Formulario{

    constructor(){
        this.puntuacion = 0;
        document.querySelector("button[type=\"submit\"]").addEventListener("click", this.analizar.bind(this));
    }

    analizar(event){
        event.preventDefault();
        this.puntuacion = 0;

        const form = event.target.closest("form");

        this.dureza = form.querySelector("input[name=\"dureza\"]").value;
        this.descripcion = form.querySelector("textarea[name=\"descripcion\"]").value;
        this.usuario = form.querySelector("input[name=\"usuario\"]").value;

        if (form.querySelector("input[name=\"numero-etapa\"]").value === "9") {
            this.puntuacion++;
        }

        if (form.querySelector("input[name=\"fecha\"]").value === "2026-08-30") {
            this.puntuacion++;
        }

        if (form.querySelector("select[name=\"salida\"]").value === "La Vila Joiosa-Villajoyosa") {
            this.puntuacion++;
        }

        if (form.querySelector("select[name=\"llegada\"]").value === "Alto de Aitana-Costa Blanca") {
            this.puntuacion++;
        }

        const tipoEtapa = form.querySelector("input[name=\"tipo-etapa\"]:checked");
        if (tipoEtapa !== null && tipoEtapa.value === "Montaña") {
            this.puntuacion++;
        }

        const puerto = form.querySelector("input[name=\"hitos\"][value=\"Puerto de montaña\"]").checked;
        const puertoEspecial = form.querySelector("input[name=\"hitos\"][value=\"Puerto categoría especial\"]").checked;
        const sprintIntermedio = form.querySelector("input[name=\"hitos\"][value=\"Sprint intermedio\"]").checked;
        const sprintBonificado = form.querySelector("input[name=\"hitos\"][value=\"Sprint bonificado\"]").checked;
        const sinHitos = form.querySelector("input[name=\"hitos\"][value=\"Sin hitos\"]").checked;
        if (puerto && !puertoEspecial && sprintIntermedio && !sprintBonificado && !sinHitos) {
            this.puntuacion++;
        }

        if (Number(form.querySelector("input[name=\"longitud\"]").value) === 187.4) {
            this.puntuacion++;
        }

        if (Number(form.querySelector("input[name=\"desnivel\"]").value) === 5166) {
            this.puntuacion++;
        }

        this.calificar();
    }

    calificar(){
        const parrafo = document.createElement("p");
        parrafo.textContent = this.usuario + " has obtenido " + this.puntuacion + " puntos, la dureza que has asignado a la etapa es " +
            this.dureza + " y tu descripción " + this.descripcion;
        document.querySelector("form").insertAdjacentElement("afterend", parrafo);
    }

}

const formulario = new Formulario();
