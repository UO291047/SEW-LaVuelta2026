# -*- coding: utf-8 -*-
"""
xml2altimetria.py

Genera el archivo altimetria.svg (perfil altimétrico de la etapa) a partir
del archivo etapaEsquema.xml. La información se extrae del árbol DOM mediante
expresiones XPath y el archivo SVG se construye con la clase Svg.

El perfil es una polilínea cerrada y rellena (efecto suelo) cuyos vértices son
la salida, los hitos, los puntos anónimos y la meta, ordenados por distancia.

Uso: python xml2altimetria.py

@version 1.0 28/Septiembre/2026
@author: David González González
"""

import os
import xml.etree.ElementTree as ET


class Punto:
    """Punto del recorrido de la etapa"""

    def __init__(self, nombre, tipo, categoria, altitud, distancia):
        self.nombre = nombre
        self.tipo = tipo              # salida, meta, puerto, sprint o anonimo
        self.categoria = categoria    # categoría del puerto o tipo de sprint
        self.altitud = altitud        # metros
        self.distancia = distancia    # km desde la salida


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

    def numero(self):
        return self.texto(self.raiz, "./uo:datosEtapa/uo:numero")

    def nombre(self):
        return self.texto(self.raiz, "./uo:datosEtapa/uo:nombre")

    def longitud(self):
        return float(self.texto(self.raiz, "./uo:datosEtapa/uo:longitudEtapa"))

    def desnivel(self):
        return self.texto(self.raiz, "./uo:datosEtapa/uo:desnivel")

    def salida(self):
        return Punto(self.texto(self.raiz, "./uo:datosEtapa/uo:ubiInicio"), "salida", "",
                     float(self.texto(self.raiz, "./uo:ubiSalida/uo:coords/uo:altitud")), 0.0)

    def meta(self):
        return Punto(self.texto(self.raiz, "./uo:datosEtapa/uo:ubiFinal"), "meta", "",
                     float(self.texto(self.raiz, "./uo:ubiMeta/uo:coords/uo:altitud")),
                     self.longitud())

    def hitos(self, clase, tipo):
        """Hitos cuyo tipoHito es 'Puerto' o 'Sprint'"""
        expresion = "./uo:hitos/uo:hito[uo:tipoHito='{}']".format(clase)
        puntos = []
        for hito in self.raiz.findall(expresion, self.NS):
            puntos.append(Punto(self.texto(hito, "./uo:nombre"), tipo,
                                hito.find("./uo:tipoHito", self.NS).get("tipo"),
                                float(self.texto(hito, "./uo:coords/uo:altitud")),
                                float(self.texto(hito, "./uo:distanciaSalida"))))
        return puntos

    def puertos(self):
        return self.hitos("Puerto", "puerto")

    def sprints(self):
        return self.hitos("Sprint", "sprint")

    def puntosAnonimos(self):
        puntos = []
        for anonimo in self.raiz.findall("./uo:puntosAnonimos/uo:puntoAnonimo", self.NS):
            puntos.append(Punto(self.texto(anonimo, "./uo:nombre"), "anonimo", "",
                                float(self.texto(anonimo, "./uo:coords/uo:altitud")),
                                float(self.texto(anonimo, "./uo:distanciaSalida"))))
        return puntos

    def recorrido(self):
        """Todos los puntos de la etapa ordenados por distancia a la salida"""
        puntos = [self.salida()] + self.puertos() + self.sprints() + self.puntosAnonimos() + [self.meta()]
        return sorted(puntos, key=lambda punto: punto.distancia)


class Svg:
    """Generación de archivos SVG con ElementTree"""

    def __init__(self, ancho, alto, titulo, descripcion):
        self.raiz = ET.Element("svg", xmlns="http://www.w3.org/2000/svg", version="1.1",
                               width=str(ancho), height=str(alto),
                               viewBox="0 0 {} {}".format(ancho, alto))
        ET.SubElement(self.raiz, "title").text = titulo
        ET.SubElement(self.raiz, "desc").text = descripcion
        self.addRect(0, 0, ancho, alto, "#ffffff")

    def addRect(self, x, y, ancho, alto, relleno):
        ET.SubElement(self.raiz, "rect", x=str(x), y=str(y), width=str(ancho), height=str(alto),
                      fill=relleno)

    def addLine(self, x1, y1, x2, y2, color, ancho, discontinua=False):
        linea = ET.SubElement(self.raiz, "line", x1=self.num(x1), y1=self.num(y1),
                              x2=self.num(x2), y2=self.num(y2), stroke=color)
        linea.set("stroke-width", str(ancho))
        if discontinua:
            linea.set("stroke-dasharray", "4 3")

    def addPolyline(self, puntos, color, ancho, relleno):
        polilinea = ET.SubElement(self.raiz, "polyline", fill=relleno, stroke=color)
        polilinea.set("stroke-width", str(ancho))
        polilinea.set("stroke-linejoin", "round")
        polilinea.set("points", " ".join("{},{}".format(self.num(x), self.num(y)) for x, y in puntos))

    def addCircle(self, cx, cy, r, relleno, borde):
        circulo = ET.SubElement(self.raiz, "circle", cx=self.num(cx), cy=self.num(cy), r=str(r),
                                fill=relleno, stroke=borde)
        circulo.set("stroke-width", "1.5")

    def addText(self, texto, x, y, tamano, anclaje="start", rotacion=0, negrita=False, color="#1a1a1a"):
        elemento = ET.SubElement(self.raiz, "text", x=self.num(x), y=self.num(y), fill=color)
        elemento.set("font-family", "Arial, Helvetica, sans-serif")
        elemento.set("font-size", str(tamano))
        elemento.set("text-anchor", anclaje)
        if negrita:
            elemento.set("font-weight", "bold")
        if rotacion:
            elemento.set("transform", "rotate({} {} {})".format(rotacion, self.num(x), self.num(y)))
        elemento.text = texto

    def num(self, valor):
        """Número con dos decimales como máximo"""
        return ("%.2f" % valor).rstrip("0").rstrip(".")

    def escribir(self, nombreArchivoSVG):
        arbol = ET.ElementTree(self.raiz)
        ET.indent(arbol)
        arbol.write(nombreArchivoSVG, encoding="utf-8", xml_declaration=True)


class Xml2Altimetria:
    """Convierte etapaEsquema.xml en altimetria.svg"""

    ANCHO = 1600
    ALTO = 720
    X_INICIO = 110           # eje de altitudes
    X_FIN = 1500             # final de la etapa
    Y_BASE = 620             # altitud 0 m
    Y_TECHO = 340            # altitud máxima de la escala
    Y_ETIQUETAS = 300        # base de las etiquetas verticales
    Y_MARCAS = 318           # marcas de puertos y sprints
    PASO_ALTITUD = 200       # separación de la escala vertical (m)
    PASO_DISTANCIA = 20      # separación de la escala horizontal (km)

    COLOR_PERFIL = "#d9381e"
    COLOR_BORDE = "#8f1d0c"
    COLORES_MARCA = {"salida": "#c00000", "meta": "#c00000", "puerto": "#1e7b34", "sprint": "#1f4fbf"}

    def __init__(self, archivoXML, archivoSVG):
        self.archivoXML = archivoXML
        self.archivoSVG = archivoSVG

    def calcularEscalas(self, etapa, recorrido):
        altitudMaxima = max(punto.altitud for punto in recorrido)
        self.altitudEscala = (int(altitudMaxima // self.PASO_ALTITUD) + 1) * self.PASO_ALTITUD
        self.longitudEtapa = etapa.longitud()

    def x(self, distancia):
        return self.X_INICIO + distancia * (self.X_FIN - self.X_INICIO) / self.longitudEtapa

    def y(self, altitud):
        return self.Y_BASE - altitud * (self.Y_BASE - self.Y_TECHO) / self.altitudEscala

    def marca(self, punto):
        """Texto de la marca de un hito: categoría del puerto o SP para los sprints"""
        if punto.tipo == "sprint":
            return "SP"
        if punto.tipo in ("salida", "meta"):
            return "S" if punto.tipo == "salida" else "M"
        if punto.categoria == "categoría especial":
            return "E"
        if punto.categoria == "bonificado":
            return "B"
        return punto.categoria[0]

    def dibujarEscalas(self, svg):
        # Líneas horizontales y escala de altitudes
        altitud = 0
        while altitud <= self.altitudEscala:
            y = self.y(altitud)
            svg.addLine(self.X_INICIO, y, self.X_FIN, y, "#d0d0d0", 1)
            svg.addText("{} m".format(altitud), self.X_INICIO - 8, y + 4, 12, "end")
            altitud += self.PASO_ALTITUD
        # Escala de distancias
        distancia = 0
        while distancia < self.longitudEtapa - self.PASO_DISTANCIA / 2:
            x = self.x(distancia)
            svg.addLine(x, self.Y_BASE, x, self.Y_BASE + 6, "#1a1a1a", 1)
            svg.addText(str(distancia), x, self.Y_BASE + 22, 12, "middle")
            distancia += self.PASO_DISTANCIA
        svg.addLine(self.X_FIN, self.Y_BASE, self.X_FIN, self.Y_BASE + 6, "#1a1a1a", 1)
        svg.addText("{} km".format(self.longitudEtapa), self.X_FIN, self.Y_BASE + 22, 12, "middle", 0, True)
        # Ejes y sus títulos
        svg.addLine(self.X_INICIO, self.Y_TECHO, self.X_INICIO, self.Y_BASE, "#1a1a1a", 1.5)
        svg.addLine(self.X_INICIO, self.Y_BASE, self.X_FIN, self.Y_BASE, "#1a1a1a", 1.5)
        svg.addText("Distancia desde la salida (km)", (self.X_INICIO + self.X_FIN) / 2, self.Y_BASE + 48,
                    14, "middle")
        svg.addText("Altitud (m)", 30, (self.Y_TECHO + self.Y_BASE) / 2, 14, "middle", -90)

    def dibujarPerfil(self, svg, recorrido):
        """Polilínea cerrada por la base para dar el efecto suelo"""
        puntos = [(self.x(0), self.Y_BASE)]
        puntos += [(self.x(p.distancia), self.y(p.altitud)) for p in recorrido]
        puntos += [(self.x(self.longitudEtapa), self.Y_BASE), (self.x(0), self.Y_BASE)]
        svg.addPolyline(puntos, self.COLOR_BORDE, 2, self.COLOR_PERFIL)

    def dibujarPuntos(self, svg, recorrido):
        """Línea vertical y texto vertical con nombre y altitud de cada punto con nombre"""
        extremos = {p.distancia: p for p in recorrido if p.tipo in ("salida", "meta")}
        for punto in recorrido:
            if not punto.nombre:
                continue
            x = self.x(punto.distancia)
            y = self.y(punto.altitud)
            principal = punto.tipo in ("salida", "meta")
            conMarca = punto.tipo in self.COLORES_MARCA
            if not principal and punto.distancia in extremos:
                # Hito situado en la salida o en la meta: solo su marca, junto a la de la salida o la meta
                desplazamiento = 24 if extremos[punto.distancia].tipo == "salida" else -24
                self.dibujarMarca(svg, punto, x + desplazamiento)
                continue
            svg.addLine(x, self.Y_MARCAS + (10 if conMarca else -12), x, y, "#6b6b6b", 1, True)
            texto = "{} / {} m".format(punto.nombre.upper() if principal else punto.nombre, round(punto.altitud))
            svg.addText(texto, x + 4, self.Y_ETIQUETAS, 12, "start", -90, principal or conMarca)
            if conMarca:
                self.dibujarMarca(svg, punto, x)

    def dibujarMarca(self, svg, punto, x):
        """Círculo de color con la categoría del puerto, SP (sprint), S (salida) o M (meta)"""
        svg.addCircle(x, self.Y_MARCAS, 10, self.COLORES_MARCA[punto.tipo], "#ffffff")
        svg.addText(self.marca(punto), x, self.Y_MARCAS + 4, 10 if punto.tipo == "sprint" else 12,
                    "middle", 0, True, "#ffffff")

    def convertir(self):
        etapa = Etapa(self.archivoXML)
        recorrido = etapa.recorrido()
        self.calcularEscalas(etapa, recorrido)

        titulo = "Altimetría de la etapa {}: {}".format(etapa.numero(), etapa.nombre())
        svg = Svg(self.ANCHO, self.ALTO, titulo,
                  "Perfil altimétrico de la etapa con la altitud de la salida, la meta, los puertos, "
                  "los sprints y los puntos intermedios en función de la distancia recorrida.")
        svg.addText(titulo, self.ANCHO / 2, 32, 20, "middle", 0, True)
        self.dibujarEscalas(svg)
        self.dibujarPerfil(svg, recorrido)
        self.dibujarPuntos(svg, recorrido)
        svg.addText("Desnivel positivo: {} m".format(etapa.desnivel()), self.ANCHO / 2, self.ALTO - 20,
                    15, "middle", 0, True)

        svg.escribir(self.archivoSVG)
        print("Creado el archivo", self.archivoSVG)

    def main(self):
        print(__doc__)
        self.convertir()


if __name__ == "__main__":
    directorio = os.path.dirname(os.path.abspath(__file__))
    Xml2Altimetria(os.path.join(directorio, "etapaEsquema.xml"),
                   os.path.join(directorio, "altimetria.svg")).main()
