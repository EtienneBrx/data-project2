from pykml import parser
from pykml.parser import Schema
from lxml import etree
import xml.etree.ElementTree as ET


if __name__ == '__main__':
    FICHIER_1 = "Polytech_mymap.xml"
    FICHIER_2 = "Polytech_earth.kml"

    with open(FICHIER_1) as file:
        doc = parser.parse(file)
        print('doc opened')

        schema_ogc = Schema("ogckml22.xsd")
        schema_gx = Schema("kml22gx.xsd")

        if schema_ogc.validate(doc):
            print("Fichier ogc")
        elif schema_gx.validate(doc):
            print("Fichier gx")
        else:
            print("Erreur format fichier")
            schema_gx.assertValid(doc)

        print(etree.tostring(doc))

        root = ET.parse(FICHIER_1).getroot()
        for root.iter("Placemark"):

