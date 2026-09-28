# -*- coding: utf-8 -*-
"""
xml2altimetria.py

Genera el archivo altimetria.svg con el perfil altimétrico de la etapa a partir
del archivo etapaEsquema.xml, usando expresiones XPath.

@version 1.0 28/Septiembre/2026
@author: David González González
"""

import xml.etree.ElementTree as ET


class Etapa:
    """Lectura de los puntos de la etapa con expresiones XPath"""

    def __init__(self, archivoXML):
        self.ns = {"uo": "http://www.uniovi.es"}
        self.raiz = ET.parse(archivoXML).getroot()

    def punto(self, elemento, nombre):
        """Devuelve (distancia, altitud, nombre) de un hito o punto anónimo"""
        distancia = float(elemento.find("./uo:distanciaSalida", self.ns).text)
        altitud = float(elemento.find("./uo:coords/uo:altitud", self.ns).text)
        return (distancia, altitud, nombre)

    def puntos(self):
        """Salida, hitos, puntos anónimos y meta ordenados por distancia"""
        salida = (0.0,
                  float(self.raiz.find("./uo:ubiSalida/uo:coords/uo:altitud", self.ns).text),
                  self.raiz.find("./uo:datosEtapa/uo:ubiInicio", self.ns).text)
        meta = (float(self.raiz.find("./uo:datosEtapa/uo:longitudEtapa", self.ns).text),
                float(self.raiz.find("./uo:ubiMeta/uo:coords/uo:altitud", self.ns).text),
                self.raiz.find("./uo:datosEtapa/uo:ubiFinal", self.ns).text)

        lista = [salida]
        for hito in self.raiz.findall("./uo:hitos/uo:hito", self.ns):
            lista.append(self.punto(hito, hito.find("./uo:nombre", self.ns).text))
        for anonimo in self.raiz.findall("./uo:puntosAnonimos/uo:puntoAnonimo", self.ns):
            lista.append(self.punto(anonimo, ""))   # los puntos anónimos no llevan texto
        lista.append(meta)

        return sorted(lista, key=lambda p: p[0])


class Svg:
    """Generación del archivo SVG"""

    def __init__(self):
        self.raiz = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", version="2.0",
                               width="1000", height="640")

    def addPolyline(self, puntos):
        texto = " ".join("{},{}".format(x, y) for x, y in puntos)
        ET.SubElement(self.raiz, "polyline", points=texto,
                      style="fill:white;stroke:red;stroke-width:4")

    def addText(self, texto, x, y):
        ET.SubElement(self.raiz, "text", x=str(x), y=str(y),
                      style="writing-mode: tb; glyph-orientation-vertical: 0;").text = texto

    def escribir(self, nombreArchivoSVG):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, encoding="UTF-8", xml_declaration=True)


class Altimetria:
    """Dibuja el perfil de la etapa"""

    def __init__(self):
        self.origen = 10      # coordenada x de la salida
        self.suelo = 420      # coordenada y de la altitud 0
        self.escalaX = 5      # píxeles por kilómetro
        self.escalaY = 0.25   # píxeles por metro

    def x(self, distancia):
        return round(self.origen + distancia * self.escalaX, 1)

    def y(self, altitud):
        return round(self.suelo - altitud * self.escalaY, 1)

    def generar(self, archivoXML, archivoSVG):
        puntos = Etapa(archivoXML).puntos()
        svg = Svg()

        # Polilínea cerrada con el suelo para dar el efecto de perfil
        vertices = [(self.x(d), self.y(a)) for d, a, n in puntos]
        vertices.append((self.x(puntos[-1][0]), self.suelo))
        vertices.append((self.origen, self.suelo))
        vertices.append(vertices[0])
        svg.addPolyline(vertices)

        # Textos verticales con el nombre de la salida, los hitos y la meta
        # (si dos puntos están en el mismo km, como el último puerto y la meta, solo se escribe el último)
        nombres = {}
        for distancia, altitud, nombre in puntos:
            if nombre:
                nombres[distancia] = nombre
        for distancia, nombre in nombres.items():
            svg.addText(nombre, self.x(distancia), self.suelo + 5)

        svg.escribir(archivoSVG)
        print("Creado el archivo", archivoSVG)


if __name__ == "__main__":
    Altimetria().generar("etapaEsquema.xml", "altimetria.svg")
