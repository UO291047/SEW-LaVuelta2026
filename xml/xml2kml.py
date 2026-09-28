# -*- coding: utf-8 -*-
"""
xml2kml.py

Genera el archivo etapa.kml (planimetría de la etapa) a partir del archivo
etapaEsquema.xml. La información se extrae del árbol DOM mediante
expresiones XPath y el archivo KML se construye con la clase Kml.

Colores de los puntos:
    - Rojo:     salida y meta
    - Verde:    puertos de montaña
    - Azul:     sprints
    - Amarillo: puntos anónimos

Uso: python xml2kml.py

@version 1.0 28/Septiembre/2026
@author: David González González
"""

import os
import xml.etree.ElementTree as ET


class Punto:
    """Punto del recorrido de la etapa"""

    def __init__(self, nombre, tipo, categoria, longitud, latitud, altitud, distancia):
        self.nombre = nombre
        self.tipo = tipo              # salida, meta, puerto, sprint o anonimo
        self.categoria = categoria    # categoría del puerto o tipo de sprint
        self.longitud = longitud
        self.latitud = latitud
        self.altitud = altitud
        self.distancia = distancia    # km desde la salida

    def coordenadas(self):
        """Coordenadas en el formato de KML: longitud,latitud,altitud"""
        return "{},{},{}".format(self.longitud, self.latitud, self.altitud)


class Etapa:
    """Lectura de etapaEsquema.xml mediante expresiones XPath"""

    NS = {"uo": "http://www.uniovi.es"}

    def __init__(self, archivoXML):
        try:
            self.raiz = ET.parse(archivoXML).getroot()
        except IOError:
            print("No se encuentra el archivo", archivoXML)
            raise SystemExit(1)
        except ET.ParseError:
            print("Error procesando el archivo XML", archivoXML)
            raise SystemExit(1)

    def texto(self, contexto, expresion):
        """Texto del elemento seleccionado por la expresión XPath"""
        elemento = contexto.find(expresion, self.NS)
        return elemento.text.strip() if elemento is not None and elemento.text else ""

    def nombre(self):
        return self.texto(self.raiz, "./uo:datosEtapa/uo:nombre")

    def crearPunto(self, contexto, nombre, tipo, categoria):
        """Crea un Punto a partir de un elemento que contiene coords y, opcionalmente, distanciaSalida"""
        longitud = float(self.texto(contexto, "./uo:coords/uo:longitud"))
        latitud = float(self.texto(contexto, "./uo:coords/uo:latitud"))
        altitud = float(self.texto(contexto, "./uo:coords/uo:altitud"))
        distancia = self.texto(contexto, "./uo:distanciaSalida")
        return Punto(nombre, tipo, categoria, longitud, latitud, altitud,
                     float(distancia) if distancia else None)

    def salida(self):
        ubicacion = self.raiz.find("./uo:ubiSalida", self.NS)
        punto = self.crearPunto(ubicacion, self.texto(self.raiz, "./uo:datosEtapa/uo:ubiInicio"),
                                "salida", "")
        punto.distancia = 0.0
        return punto

    def meta(self):
        ubicacion = self.raiz.find("./uo:ubiMeta", self.NS)
        punto = self.crearPunto(ubicacion, self.texto(self.raiz, "./uo:datosEtapa/uo:ubiFinal"),
                                "meta", "")
        punto.distancia = float(self.texto(self.raiz, "./uo:datosEtapa/uo:longitudEtapa"))
        return punto

    def hitos(self, clase, tipo):
        """Hitos cuyo tipoHito es 'Puerto' o 'Sprint'"""
        expresion = "./uo:hitos/uo:hito[uo:tipoHito='{}']".format(clase)
        puntos = []
        for hito in self.raiz.findall(expresion, self.NS):
            categoria = hito.find("./uo:tipoHito", self.NS).get("tipo")
            puntos.append(self.crearPunto(hito, self.texto(hito, "./uo:nombre"), tipo, categoria))
        return puntos

    def puertos(self):
        return self.hitos("Puerto", "puerto")

    def sprints(self):
        return self.hitos("Sprint", "sprint")

    def puntosAnonimos(self):
        puntos = []
        for anonimo in self.raiz.findall("./uo:puntosAnonimos/uo:puntoAnonimo", self.NS):
            puntos.append(self.crearPunto(anonimo, self.texto(anonimo, "./uo:nombre"), "anonimo", ""))
        return puntos

    def recorrido(self):
        """Todos los puntos de la etapa ordenados por distancia a la salida"""
        puntos = [self.salida()] + self.puertos() + self.sprints() + self.puntosAnonimos() + [self.meta()]
        return sorted(puntos, key=lambda punto: punto.distancia)


class Kml:
    """Generación de archivos KML con ElementTree"""

    def __init__(self, nombre):
        self.raiz = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, "Document")
        ET.SubElement(self.doc, "name").text = nombre

    def addEstiloPunto(self, identificador, color):
        """Estilo de icono. El color KML tiene el formato aabbggrr"""
        estilo = ET.SubElement(self.doc, "Style", id=identificador)
        icono = ET.SubElement(estilo, "IconStyle")
        ET.SubElement(icono, "color").text = color
        ET.SubElement(icono, "scale").text = "1.1"
        imagen = ET.SubElement(icono, "Icon")
        ET.SubElement(imagen, "href").text = "http://maps.google.com/mapfiles/kml/paddle/wht-blank.png"

    def addEstiloLinea(self, identificador, color, ancho):
        estilo = ET.SubElement(self.doc, "Style", id=identificador)
        linea = ET.SubElement(estilo, "LineStyle")
        ET.SubElement(linea, "color").text = color
        ET.SubElement(linea, "width").text = str(ancho)

    def addPlacemark(self, nombre, descripcion, coordenadas, estilo):
        pm = ET.SubElement(self.doc, "Placemark")
        ET.SubElement(pm, "name").text = nombre
        ET.SubElement(pm, "description").text = descripcion
        ET.SubElement(pm, "styleUrl").text = "#" + estilo
        punto = ET.SubElement(pm, "Point")
        ET.SubElement(punto, "altitudeMode").text = "clampToGround"
        ET.SubElement(punto, "coordinates").text = coordenadas

    def addLineString(self, nombre, listaCoordenadas, estilo):
        pm = ET.SubElement(self.doc, "Placemark")
        ET.SubElement(pm, "name").text = nombre
        ET.SubElement(pm, "styleUrl").text = "#" + estilo
        ls = ET.SubElement(pm, "LineString")
        ET.SubElement(ls, "extrude").text = "1"
        ET.SubElement(ls, "tessellate").text = "1"
        ET.SubElement(ls, "altitudeMode").text = "clampToGround"
        ET.SubElement(ls, "coordinates").text = "\n" + "\n".join(listaCoordenadas) + "\n"

    def escribir(self, nombreArchivoKML):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding="utf-8", xml_declaration=True)


class Xml2Kml:
    """Convierte etapaEsquema.xml en etapa.kml"""

    # Colores en formato KML (aabbggrr)
    ESTILOS = {
        "salida": ("estiloSalidaMeta", "ff0000ff"),   # rojo
        "meta": ("estiloSalidaMeta", "ff0000ff"),     # rojo
        "puerto": ("estiloPuerto", "ff00ff00"),       # verde
        "sprint": ("estiloSprint", "ffff0000"),       # azul
        "anonimo": ("estiloAnonimo", "ff00ffff"),     # amarillo
    }

    def __init__(self, archivoXML, archivoKML):
        self.archivoXML = archivoXML
        self.archivoKML = archivoKML

    def descripcion(self, punto):
        texto = "Km {} - Altitud {} m".format(punto.distancia, punto.altitud)
        if punto.categoria:
            texto = punto.categoria + " - " + texto
        return texto

    def convertir(self):
        etapa = Etapa(self.archivoXML)
        recorrido = etapa.recorrido()

        kml = Kml("Etapa: " + etapa.nombre())
        for identificador, color in dict.fromkeys(self.ESTILOS.values()):
            kml.addEstiloPunto(identificador, color)
        kml.addEstiloLinea("estiloRecorrido", "ff0000ff", 4)

        kml.addLineString("Recorrido de la etapa", [p.coordenadas() for p in recorrido], "estiloRecorrido")
        for punto in recorrido:
            nombre = punto.nombre if punto.nombre else "Km {}".format(punto.distancia)
            kml.addPlacemark(nombre, self.descripcion(punto), punto.coordenadas(),
                             self.ESTILOS[punto.tipo][0])

        kml.escribir(self.archivoKML)
        print("Creado el archivo", self.archivoKML)

    def main(self):
        print(__doc__)
        self.convertir()


if __name__ == "__main__":
    directorio = os.path.dirname(os.path.abspath(__file__))
    Xml2Kml(os.path.join(directorio, "etapaEsquema.xml"),
            os.path.join(directorio, "etapa.kml")).main()
