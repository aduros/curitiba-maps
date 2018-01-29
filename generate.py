#!/usr/bin/env python

import dbf
from osgeo import ogr, osr

def generate (filePrefix, layerName, itemName=None, metadata={}):
    table = dbf.Table("data/"+filePrefix+".dbf")
    table.open()

    sourceData = ogr.GetDriverByName("ESRI Shapefile").Open("data/"+filePrefix+".shp", 0)
    sourceLayer = sourceData.GetLayer()

    sourceProj = osr.SpatialReference()
    sourceProj.ImportFromEPSG(29192)
    targetProj = osr.SpatialReference()
    targetProj.ImportFromEPSG(4326)
    transform = osr.CoordinateTransformation(sourceProj, targetProj)

    kml = ogr.GetDriverByName("KML").CreateDataSource("data/"+filePrefix+".kml")
    layer = kml.CreateLayer(layerName)
    features = []

    print(filePrefix+" --> "+" ".join(table.structure()))
    print("")

    for key in metadata:
        layer.CreateField(ogr.FieldDefn(key, ogr.OFTString))

    count = 0
    for record in table:
        feature = ogr.Feature(layer.GetLayerDefn())
        print(record)
        # print(record.equipament)

        try:
            name = record["nome"].strip().title()
            feature.SetField("name", name.encode("utf8"))
        except dbf.ver_2.FieldMissingError:
            if itemName is not None:
                feature.SetField("name", itemName)

        for key in metadata:
            value = (""+record[metadata[key]]).strip().title()
            feature.SetField(key, value.encode("utf8"))

        try:
            lat = record["lat_sirgas"]
            lon = record["lon_sirgas"]
            geom = ogr.Geometry(ogr.wkbPoint)
            geom.AddPoint(lon, lat)
        except dbf.ver_2.FieldMissingError:
            sourceFeature = sourceLayer.GetFeature(count)
            geom = sourceFeature.GetGeometryRef()
            geom.Transform(transform)

        feature.SetGeometry(geom)
        features.append(feature)
        count = count + 1

    features.sort(key=lambda feature: feature.GetField("name"))
    for feature in features:
        layer.CreateFeature(feature)

generate("ACADEMIA_AO_AR_LIVRE", "Academias ao Ar Livre")

generate("PARQUES_E_BOSQUES", "Parques e Bosques", metadata={
    "Tipo": "tipo",
})
generate("PRACAS_E_JARDINETES", "Pracas e Jardinetes", metadata={
    "Tipo": "tipo",
}) # TODO(bruno): Spelling

generate("CALCADAO", "Calcadao")

# generate("CICLOVIA_OFICIAL", "Ciclovias")
# generate("CICLORROTA", "Ciclorrotas")
# generate("PARACICLO", "Paraciclos", itemName="Paraciclo", metadata={
#     "Capacidade": "capacidade",
# })

# generate("CENTRO_DE_ESPORTE_E_LAZER", "Centros de Esporte e Lazer", metadata={
#     "Telefone": "telefone",
# })
# generate("CENTRO_DE_ATIVIDADE_FISICA", "Centros de Atividade Fisica", metadata={
#     "Telefone": "telefone",
# })

# generate("RUA_DA_CIDADANIA", "Ruas da Cidadania")
# generate("CLUBE_DA_GENTE", "Clubes da Gente", metadata={
#     "Telefone": "telefone",
# })
