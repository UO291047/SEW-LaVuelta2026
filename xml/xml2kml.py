# -*- coding: utf-8 -*-
"""
xml2kml.py

Genera el archivo etapa.kml con la planimetría de la etapa a partir del
archivo etapaEsquema.xml, usando expresiones XPath.

Colores (según el guion): rojo salida y meta, verde puertos de montaña,
azul sprints y amarillo puntos anónimos.

@version 1.0 28/Septiembre/2026
@author: David González González
"""

import xml.etree.ElementTree as ET

# Colores KML en formato aabbggrr
ROJO = "ff0000ff"
VERDE = "ff00ff00"
AZUL = "ffff0000"
AMARILLO = "ff00ffff"


class Etapa:
    """Lectura de los puntos de la etapa con expresiones XPath"""

    def __init__(self, archivoXML):
        self.ns = {"uo": "http://www.uniovi.es"}
        self.raiz = ET.parse(archivoXML).getroot()

    def punto(self, elemento, nombre, color, distancia):
        """Devuelve (distancia, coordenadas, nombre, color) de un elemento con coords"""
        longitud = elemento.find("./uo:coords/uo:longitud", self.ns).text
        latitud = elemento.find("./uo:coords/uo:latitud", self.ns).text
        altitud = elemento.find("./uo:coords/uo:altitud", self.ns).text
        return (distancia, longitud + "," + latitud + "," + altitud, nombre, color)

    def hito(self, elemento, color):
        nombre = elemento.find("./uo:nombre", self.ns)
        distancia = float(elemento.find("./uo:distanciaSalida", self.ns).text)
        return self.punto(elemento, nombre.text if nombre is not None else "", color, distancia)

    def puntos(self):
        """Salida, hitos, puntos anónimos y meta ordenados por distancia"""
        lista = [self.punto(self.raiz.find("./uo:ubiSalida", self.ns),
                            self.raiz.find("./uo:datosEtapa/uo:ubiInicio", self.ns).text, ROJO, 0.0)]

        for puerto in self.raiz.findall("./uo:hitos/uo:hito[uo:tipoHito='Puerto']", self.ns):
            lista.append(self.hito(puerto, VERDE))
        for sprint in self.raiz.findall("./uo:hitos/uo:hito[uo:tipoHito='Sprint']", self.ns):
            lista.append(self.hito(sprint, AZUL))
        for anonimo in self.raiz.findall("./uo:puntosAnonimos/uo:puntoAnonimo", self.ns):
            lista.append(self.hito(anonimo, AMARILLO))

        lista.append(self.punto(self.raiz.find("./uo:ubiMeta", self.ns),
                                self.raiz.find("./uo:datosEtapa/uo:ubiFinal", self.ns).text, ROJO,
                                float(self.raiz.find("./uo:datosEtapa/uo:longitudEtapa", self.ns).text)))

        return sorted(lista, key=lambda p: p[0])


class Kml:
    """Generación del archivo KML"""

    def __init__(self):
        self.raiz = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        self.doc = ET.SubElement(self.raiz, "Document")

    def addPlacemark(self, nombre, coordenadas, color):
        pm = ET.SubElement(self.doc, "Placemark")
        ET.SubElement(pm, "name").text = nombre
        icono = ET.SubElement(ET.SubElement(pm, "Style"), "IconStyle")
        ET.SubElement(icono, "color").text = color
        ET.SubElement(ET.SubElement(pm, "Point"), "coordinates").text = coordenadas

    def addLineString(self, listaCoordenadas):
        pm = ET.SubElement(self.doc, "Placemark")
        ET.SubElement(pm, "name").text = "Recorrido"
        linea = ET.SubElement(ET.SubElement(pm, "Style"), "LineStyle")
        ET.SubElement(linea, "color").text = ROJO
        ET.SubElement(linea, "width").text = "4"
        ls = ET.SubElement(pm, "LineString")
        ET.SubElement(ls, "tessellate").text = "1"
        ET.SubElement(ls, "coordinates").text = "\n".join(listaCoordenadas)

    def escribir(self, nombreArchivoKML):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoKML, encoding="UTF-8", xml_declaration=True)


class Planimetria:
    """Dibuja el recorrido de la etapa y sus puntos"""

    def generar(self, archivoXML, archivoKML):
        puntos = Etapa(archivoXML).puntos()
        kml = Kml()

        kml.addLineString([coordenadas for d, coordenadas, n, c in puntos])
        for distancia, coordenadas, nombre, color in puntos:
            kml.addPlacemark(nombre, coordenadas, color)

        kml.escribir(archivoKML)
        print("Creado el archivo", archivoKML)


if __name__ == "__main__":
    Planimetria().generar("etapaEsquema.xml", "etapa.kml")
