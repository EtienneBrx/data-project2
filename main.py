from pykml import parser
from pykml.parser import Schema
from lxml import etree


if __name__ == '__main__':
    FICHIER_1 = "Polytech_mymap.xml"
    FICHIER_2 = "Polytech_earth.kml"

    demandes_map = {"parking" : 0,
                    "parc": 0,
                    "potager": 0,
                    "piscine":0,
                    "ressourcerie": 0,
                    "gymnase":0,
                    "terrain de sport":0,
                    "place":0
                    }
    polygones = []

    with open(FICHIER_1) as file:
        doc = parser.parse(file).getroot()
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

        #print(etree.tostring(doc))
        print(doc.Document.name)

        for pm in doc.Document.Placemark:
            # print(pm.name)
            if str(pm.name).lower() in demandes_map.keys():
                demandes_map[str(pm.name).lower()] += 1
                # print(pm.Polygon.outerBoundaryIs.LinearRing.coordinates)
                polygones.append(pm)

        print(demandes_map)
        print(len(polygones))


