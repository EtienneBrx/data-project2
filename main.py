from pykml import parser
from pykml.parser import Schema
from lxml import etree
from shapely.geometry.polygon import LinearRing


polygones = []
polygones_shapely = []
poly_valid = []
demandes_map = {"parking": 0,
                "parc": 0,
                "potager": 0,
                "piscine": 0,
                "ressourcerie": 0,
                "gymnase": 0,
                "terrain de sport": 0,
                "place": 0
                }


def has_collision():
    # parcours de toutes les demandes
    for key in sorted(demandes_map, key=demandes_map.get, reverse=True):
        # parcours des formes correspondantes
        for j in range(0, len(polygones_shapely)):
            if str(polygones_shapely[j]["name"]).lower() == key:
                # parcours des polygones placés
                if len(poly_valid) <= 0:
                    poly_valid.append(polygones_shapely[j])
                else:
                    for v in poly_valid:
                        if not polygones_shapely[j]["poly"].overlaps(v):
                            poly_valid.append(polygones_shapely[j])


if __name__ == '__main__':
    FICHIER_1 = "Polytech_mymap.xml"
    FICHIER_2 = "Polytech_earth.kml"

    with open("Projet_2_-_Echange_de_donnees.kml") as file:
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
            # schema_gx.assertValid(doc)

        # print(etree.tostring(doc))
        print(doc.Document.name)

        for pm in doc.Document.Placemark:
            # print(pm.name)
            if str(pm.name).lower() in demandes_map.keys():
                demandes_map[str(pm.name).lower()] += 1
                polygones.append(pm)
                # Récupération forme en Shapely
                coord_str = pm.Polygon.outerBoundaryIs.LinearRing.coordinates
                coord_str_list = str(coord_str).split()
                coord_tuples = []
                for string in coord_str_list:
                    floats = string.split(',')
                    coord_tuples.append((float(floats[0]), float(floats[1])))
                polygones_shapely.append({
                    "poly": LinearRing(coord_tuples),
                    "name": str(pm.name).lower()
                })

        # Sélection emplacements
        has_collision()

        print(demandes_map)
        print(len(polygones))
        print(poly_valid)


