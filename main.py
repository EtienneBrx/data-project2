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


# Valide le fichier selon le bon schéma
def validate_file(file):
    schema_ogc = Schema("ogckml22.xsd")
    schema_gx = Schema("kml22gx.xsd")
    if schema_ogc.validate(doc):
        print("Fichier ogc")
    elif schema_gx.validate(doc):
        print("Fichier gx")
    else:
        print("Erreur format fichier")
        # schema_gx.assertValid(doc)


def write_file(doc):
    with open('Carte_résulats.kml', 'w') as output:
        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<kml>\n<Document>\n')
        # Écrit les styles
        for style_map in doc.Document.StyleMap:
            output.write(etree.tostring(style_map, pretty_print=True).decode("utf-8"))
            output.write('\n')
        if hasattr(doc.Document, 'Style'):
            for style_tag in doc.Document.Style:
                output.write(etree.tostring(style_tag, pretty_print=True).decode("utf-8"))
                output.write('\n')
        elif hasattr(doc.Document, 'gx:CascadingStyle'):
            for style_tag in doc.Document['gx:CascadingStyle']:
                output.write(etree.tostring(style_tag, pretty_print=True).decode("utf-8"))
                output.write('\n')
        # Écrit les placemarks
        for poly_result in poly_valid:
            output.write(etree.tostring(poly_result['placemark'], pretty_print=True).decode("utf-8"))
            output.write('\n')
        output.write('\n</Document>\n</kml>')


if __name__ == '__main__':
    FICHIER_1 = "Polytech_mymap.xml"
    FICHIER_2 = "Polytech_earth.kml"
    FICHIER_3 = "simple.kml"
    FICHIER_4 = "Carte 6.kml"
    FICHIER_5 = "Carte 7.kml"

    with open(FICHIER_3) as file:
        doc = parser.parse(file).getroot()
        print('file opened: ' + file.name)
        validate_file(file)
        print('document: ' + doc.Document.name)
        # print(etree.tostring(doc, pretty_print=True).decode("utf-8"))

        # Parcours des formes dans le fichier kml
        if hasattr(doc.Document, 'Placemark'):
            placemarks = doc.Document.Placemark
        else:
            placemarks = doc.Document.Folder.Placemark

        for pm in placemarks:
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
                    "name": str(pm.name).lower(),
                    "placemark": pm
                })

        print(demandes_map)

        # Sélection emplacements
        has_collision()
        print(len(polygones_shapely))
        print(polygones_shapely)
        print(len(poly_valid))
        print(poly_valid)

        # Écriture fichier
        write_file(doc)
        print('finished')
