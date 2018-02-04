#!/usr/bin/env python
# coding=utf8

import dbf
from osgeo import ogr, osr

class Generator:
    def __init__ (self, name, metadata={}):
        self.name = name
        self.metadata = metadata
        self.features = []

        sourceProj = osr.SpatialReference()
        sourceProj.ImportFromEPSG(29192)
        targetProj = osr.SpatialReference()
        targetProj.ImportFromEPSG(4326)
        self.transform = osr.CoordinateTransformation(sourceProj, targetProj)

        self.kml = ogr.GetDriverByName("KML").CreateDataSource("output/"+name+".kml")
        self.layer = self.kml.CreateLayer(name)

        self.layer.CreateField(ogr.FieldDefn("categoria", ogr.OFTString))
        for key in metadata:
            self.layer.CreateField(ogr.FieldDefn(key, ogr.OFTString))

    def addFeatures (self, filePrefix, defaultName=None):
        table = dbf.Table("data/"+filePrefix+".dbf")
        table.open()

        sourceData = ogr.GetDriverByName("ESRI Shapefile").Open("data/"+filePrefix+".shp", 0)
        sourceLayer = sourceData.GetLayer()

        count = 0
        for record in table:
            feature = ogr.Feature(self.layer.GetLayerDefn())
            # print(record)

            try:
                name = record["nome"].strip().title()
                feature.SetField("name", name.encode("utf8"))
            except dbf.ver_2.FieldMissingError:
                if defaultName is not None:
                    feature.SetField("name", defaultName)

            for key in self.metadata:
                try:
                    value = (""+record[self.metadata[key]]).strip().title()
                    feature.SetField(key, value.encode("utf8"))
                except dbf.ver_2.FieldMissingError:
                    pass

            if defaultName is not None:
                feature.SetField("categoria", defaultName)

            try:
                lat = record["lat_sirgas"]
                lon = record["lon_sirgas"]
                geom = ogr.Geometry(ogr.wkbPoint)
                geom.AddPoint(lon, lat)
            except dbf.ver_2.FieldMissingError:
                sourceFeature = sourceLayer.GetFeature(count)
                geom = sourceFeature.GetGeometryRef()
                geom.Transform(self.transform)

            feature.SetGeometry(geom)
            self.features.append(feature)
            count = count + 1

    def write (self):
        self.features.sort(key=lambda feature: feature.GetField("name"))
        for feature in self.features:
            self.layer.CreateFeature(feature)

#
# Parks and Recreation
#

generator = Generator("Parques e Bosques", metadata={"tipo": "tipo"})
generator.addFeatures("PARQUES_E_BOSQUES")
generator.write()

generator = Generator("Praças e Jardinetes", metadata={"tipo": "tipo"})
generator.addFeatures("PRACAS_E_JARDINETES")
generator.write()

generator = Generator("Calçadões")
generator.addFeatures("CALCADAO", "Calçadão")
generator.write()

generator = Generator("Ciclovias", metadata={"tipo": "tipo"})
generator.addFeatures("CICLOVIA_OFICIAL", "Ciclovia")
# generator.addFeatures("CICLORROTA", "Ciclorrota")
generator.addFeatures("PARACICLO", "Paraciclo")
generator.write()

generator = Generator("Clubes de Esporte", metadata={"telefone": "telefone"})
generator.addFeatures("CENTRO_DE_ESPORTE_E_LAZER", "Centro de Esporte e Lazer")
generator.addFeatures("CENTRO_DE_ATIVIDADE_FISICA", "Centro de Atividade Fisica")
generator.addFeatures("CENTRO_DA_JUVENTUDE", "Centro da Juventude")
generator.addFeatures("CLUBE_DA_GENTE", "Clube da Gente")
generator.write()

generator = Generator("Academias ao Ar Livre")
generator.addFeatures("ACADEMIA_AO_AR_LIVRE")
generator.write()

#
# Health and Services
#

generator = Generator("Emergências", metadata={"24 horas?": "func_24hr", "telefone": "telefone", "email": "email", "site": "site"})
generator.addFeatures("HOSPITAL", "Hospitals")
generator.addFeatures("UNIDADE_DE_PRONTO_ATENDIMENTO", "Unidade de Pronto Atendimento")
generator.write()

generator = Generator("Médicos")
generator.addFeatures("UNIDADE_DE_SAUDE", "Unidades de Saúde")
generator.addFeatures("CENTRO_DE_ESPECIALIDADES_MEDICAS", "Centro de Especialidades Médicas")
generator.addFeatures("CENTRO_DE_ESPECIALIDADES_ODONTOLOGICAS", "Centro de Especialidades Odontológicas")
generator.addFeatures("CAPS", "Centro de Atendimento Psicosocial (CAPS)")
generator.write()

generator = Generator("Creches", metadata={"telefone": "telefone", "email": "email"})
generator.addFeatures("CMEI", "Creche Municipal (CMEI)")
generator.addFeatures("CEI_CONVENIADA", "Creche Conveniada (CEI)")
generator.write()

generator = Generator("Escolas", metadata={"telefone": "telefone", "email": "email"})
generator.addFeatures("ESCOLA_MUNICIPAL", "Escola Municipal")
generator.write()

generator = Generator("Serviços Social", metadata={"telefone": "telefone", "email": "email"})
generator.addFeatures("RUA_DA_CIDADANIA", "Rua da Cidadania")
generator.addFeatures("CRAS", "Centro de Referência da Assistência Social (CRAS)")
generator.addFeatures("CENTRO_DA_JUVENTUDE", "Centro da Juventude")
generator.addFeatures("CLUBE_DA_GENTE", "Clube da Gente")
generator.write()
