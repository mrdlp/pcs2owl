#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
eco11.py

eCl@ss 11.X import module

Created by Miguel Ramos on 2021-05-06 based on Alexander Stolz's work.
"""
import codecs
import csv

from util import *  # imports also config, classes, rdflib, ...
import util


def importData():
    """Loading facility"""
    print "Step 1: Loading PCS from %s" % __name__

    # ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
    util.metadata = Ontology("eClass 11.0", creator="Miguel Ramos",
                             contributor="Alexander Stolz, Martin Hepp, Andreas Radinger", version="1.0")

    # class synonyms
    names = {}
    print "loading class synonyms"
    synonym_en = csv.reader(open("pcs/eco11/eClass11_1_KW_en.csv", "r"), delimiter=";")
    for line in list(synonym_en)[1:]:
        idcl = line[3]  # IdCC/IdPR
        desc = line[4]  # KeywordValue/SynonymValue
        if not idcl in names:
            names[idcl] = []
        names[idcl].append(desc)

    codes = {}
    print "loading classes"
    artclass = csv.reader(open("pcs/eco11/eClass11_1_CC_en.csv", "r"), delimiter=";")
    for line in list(artclass)[1:]:
        # CLASS: def __init__(self, parent_id, class_id, label="", description=""):
        idcl = line[1]  # IdCC
        code = line[6]  # CodedName e.g. 13000000
        desc = line[7]  # PreferredName
        codes[code] = idcl  # append idcl with key of coded name
        if not idcl in names:
            names[idcl] = []
        names[idcl].append(desc)
        for k in range(0, len(code), 2):
            check = "00"
            if k == 0:  # :-k with 0 would be understood incorrectly
                check = code[-2:]
            else:
                check = code[:-k][-2:]
            # print "len", len(code), "k", k, "test", check
            if check != "00":
                parent = code[:-k - 2] + "0" * (k + 2)
                if parent in codes:
                    # print "%s (%s) is parent of %s (%s)" %(parent, codes[parent], code, codes[code])
                    break
        # save hierarchy code e.g. hc = 13000000
        hc = code
        code = codes[code]
        if parent == "00000000":
            parent = None
        else:
            pass
            parent = codes[parent]
        # print parent, code, desc
        cappend(Class(parent, code, desc, desc, synonyms={"en": names[idcl]}, hierarchy_code=hc))

    # feature
    # PROPERTY: def __init__(self, class_id, prop_id, label="", description="", prop_type=["qualitative", "string"]):
    feature2classes = {}
    print "loading feature2classes mapping"
    class2featuremap = csv.reader(open("pcs/eco11/eClass11_1_CC_PR_en.csv", "r"), delimiter=";")
    for line in list(class2featuremap)[1:]:
        idcl = line[1]  # IdCC
        idatt = line[4]  # IdPR
        if idatt not in feature2classes:
            feature2classes[idatt] = []
        feature2classes[idatt].append(idcl)

    print "loading units"
    unit_dic = {}
    units = csv.reader(open("pcs/eco11/eClass11_0_UN_en.csv", "r"), delimiter=";")
    for line in list(units)[1:]:
        unit_name = line[0]                 # PreferredName
        unit_symbol = line[1]               # ShortName
        unit_symbol_SI = line[5]            # SINotation
        unit_name_SI = line[6]              # SIName
        unit_id = line[12]                   # IrdiUN
        uname = unit_name_SI if unit_name_SI and unit_name_SI != "kein Eintrag" else unit_name
        usymbol = unit_symbol_SI if unit_symbol_SI and unit_symbol_SI != "kein Eintrag" else unit_symbol
        unit_dic[unit_id] = {"name": uname, "symbol": usymbol}

    feature2type = {}
    print "loading features"
    feature = csv.reader(open("pcs/eco11/eClass11_1_PR_en.csv", "r"), delimiter=";")
    for line in list(feature)[1:]:
        idatt = line[1]                                                 # IdPR
        domain = []
        if idatt in feature2classes:
            domain = feature2classes[idatt]
        label = line[6]                                                 # PreferredName
        description = line[8]                                           # Definition
        pp_unit_id = line[13]                                           # IrdiUN
        pp_unit_name = unit_dic.get(pp_unit_id, {}).get("name")         # Unit name
        pp_unit_symbol = unit_dic.get(pp_unit_id, {}).get("symbol")     # Unit symbol
        format = line[19]                                               # DataType
        symbol = line[15]  # e.g. mm for millimetres					# ISOCountryCode
        uom = line[16]  # e.g. MMT for millimetres					    # Category
        attribute_type = line[17]  # e.g. direct (es erfolgt ein freier Eintrag) or indirect (Werte sind vorhanden)
        valency = line[
            21]  # e.g. univalent (es wird genau ein Wert zugeordnet) or multivalent (Werte unbestimmter Anzahl werden zugeordnet)
        if not idatt in names:
            names[idatt] = []

        Datatype2Format = {"STRING_TRANSLATABLE": {"object_type": "datatype", "datatype": "string" },
                           "STRING": {"object_type": "datatype", "datatype": "string"},
                           "BOOLEAN": {"object_type": "datatype", "datatype": "boolean"},
                           "DATE": {"object_type": "datatype", "datatype": "date"},
                           "REAL_MEASURE": {"object_type": "quantitative", "datatype": "float" },
                           "RATIONAL_MEASURE": {"object_type": "quantitative", "datatype": "float"},
                           "INTEGER_MEASURE": {"object_type": "quantitative", "datatype": "integer" },
                           "REAL_COUNT": {"object_type": "datatype", "datatype": "float" },
                           "INTEGER_COUNT": {"object_type": "datatype", "datatype": "integer"}}

        datatype = Datatype2Format.get(format, {}).get("datatype")
        object_type = Datatype2Format.get(format, {}).get("object_type")

        # http://www.heppnetz.de/projects/eclassowl/#gentax-properties
        if not datatype or attribute_type == "indirect":
            datatype = "string"
            object_type = "qualitative"

        feature2type[idatt] = {}
        feature2type[idatt]["object_type"] = object_type
        feature2type[idatt]["datatype"] = datatype

        if len(domain) > 0:
            for d in domain:
                pappend(Property(d, idatt, label, description, prop_type=[object_type, datatype],
                                 synonyms={"en": names[idatt]}, UnitOfMeasurementName=pp_unit_name,
                                 UnitOfMeasurementSymbol=pp_unit_symbol))
        else:
            # print "could not determine domain for property", idatt, "- domain:", domain
            pappend(Property(None, idatt, label, description, prop_type=[object_type, datatype],
                             synonyms={"en": names[idatt]}, UnitOfMeasurementName=pp_unit_name,
                             UnitOfMeasurementSymbol=pp_unit_symbol))

    value2features = {}
    print "loading features2value mapping"
    feature2valuemap = csv.reader(open("pcs/eco11/eClass11_1_PR_VA_en.csv", "r"), delimiter=";")
    for line in list(feature2valuemap)[1:]:
        idatt = line[0]
        idvl = line[1]
        if idvl not in value2features:
            value2features[idvl] = []
        value2features[idvl].append(idatt)

    # INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description="", inst_type=""):
    print "loading values"
    value = csv.reader(open("pcs/eco11/eClass11_1_VA_en.csv", "r"), delimiter=";")
    for line in list(value)[1:]:
        idvl = line[1]  # IdVA
        label = line[6]  # PreferredName
        description = line[8]  # Definition
        if line[8]:
            description = line[8]
        if idvl in value2features:
            for feature in value2features[idvl]:
                if feature in feature2type:
                    iappend(Individual(feature, idvl, label, description,
                                       [feature2type[feature]["object_type"], feature2type[feature]["datatype"]]))
                else:
                    iappend(Individual(feature, idvl, label, description))


def convert2OWL(element_type=None):
    """Dummy function, see util.py"""
    util.convert2OWL(element_type)


def serialize(format="", filename=None):
    """Dummy function, see util.py"""
    util.serialize(format, filename)
