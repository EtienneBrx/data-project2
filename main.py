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
        for polygon in polygones_shapely:
            if str(polygon["name"]).lower() == key:
                # parcours des polygones placés
                print("poly", polygon)
                if len(poly_valid) <= 0:
                    poly_valid.append(polygon)
                elif not already_valid(polygon):
                    is_valid = True
                    intersects_with = [polygon]
                    for v in poly_valid:
                        intersects = polygon["poly"].intersects(v['poly'])
                        if polygon["poly"] == v['poly'] or intersects:
                            is_valid = False
                            if intersects:
                                intersects_with.append(v)
                    keep_most_demanded(intersects_with)


def keep_most_demanded(shape_with_collison):
    global poly_valid
    max_shape = shape_with_collison[0]
    for shape in shape_with_collison:
        if demandes_map[shape['name']] > demandes_map[max_shape['name']]:
            max_shape = shape
    shapes_to_remove = []
    for shape_to_remove in shape_with_collison:
        if shape_to_remove['poly'] != max_shape['poly']:
            shapes_to_remove.append(shape_to_remove['poly'])
    new_valid = [max_shape]
    for valid in poly_valid:
        if valid['poly'] not in shapes_to_remove and max_shape['poly'] != valid['poly']:
            new_valid.append(valid)
    poly_valid = new_valid


def already_valid(polygon):
    for poly in poly_valid:
        if poly['poly'] == polygon['poly']:
            return True
    return False


if __name__ == '__main__':
    FICHIER_1 = "Polytech_mymap.xml"
    FICHIER_2 = "Polytech_earth.kml"
    FICHIER_3 = "simple.kml"

    with open(FICHIER_3) as file:
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

        print(demandes_map)

        # Sélection emplacements
        has_collision()
        print(len(polygones_shapely))
        print(polygones_shapely)
        print(len(poly_valid))
        print(poly_valid)


