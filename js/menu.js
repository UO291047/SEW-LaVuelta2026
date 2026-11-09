"use strict";

class Menu{

    constructor(){
        this.boton = document.querySelector("header > button");
        this.menu = document.querySelector("nav");
        this.boton.addEventListener("click", this.desplegar.bind(this));
    }

    desplegar(){
        const abierto = this.menu.classList.toggle("abierto");
        this.boton.textContent = abierto ? "x" : "☰";
        this.boton.setAttribute("aria-expanded", abierto);
    }

}

const menu = new Menu();
