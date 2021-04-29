#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
eco5.py

eCl@ss 5.X import module

Created by Alex Stolz on 2011-03-25.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs
import csv

from util import * # imports also config, classes, rdflib, ...
import util

def importData():
	"""Loading facility"""
	print "Step 1: Loading PCS from %s" % __name__
	
	# ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
	util.metadata = Ontology("eClass 5.1.4", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	# class synonyms
	names = {}
	print "loading class synonyms"
	synonym_de = csv.reader(open("pcs/eco5/eClass5_1_4_sw_de.csv", "r"), delimiter=";")
	for line in list(synonym_de)[1:]:
		idcl = line[1]
		desc = line[3]
		if not idcl in names:
			names[idcl] = []
		names[idcl].append(desc)
	
	codes = {}
	print "loading classes"
	artclass = csv.reader(open("pcs/eco5/eClass5_1_4_de.csv", "r"), delimiter=";")
	for line in list(artclass)[1:]:
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		idcl = line[0]
		code = line[5]
		desc = line[6]
		codes[code] = idcl # append idcl with key of coded name
		if not idcl in names:
			names[idcl] = []
		names[idcl].append(desc)
		for k in range(0, len(code), 2):
			check = "00"
			if k == 0: # :-k with 0 would be understood incorrectly
				check = code[-2:]
			else:
				check = code[:-k][-2:]
			#print "len", len(code), "k", k, "test", check
			if check != "00":
				parent = code[:-k-2]+"0"*(k+2)
				if parent in codes:
					#print "%s (%s) is parent of %s (%s)" %(parent, codes[parent], code, codes[code])
					break
		code = codes[code]
		if parent == "00000000":
			parent = None
		else:
			parent = codes[parent]
		cappend(Class(parent, code, desc, synonyms={"de":names[idcl]}))
	
	# feature
	# PROPERTY: def __init__(self, class_id, prop_id, label="", description="", prop_type=["qualitative", "string"]):
	feature2classes = {}
	print "loading feature2classes mapping"
	class2featuremap = csv.reader(open("pcs/eco5/eClass5_1_4_ml_de.csv", "r"), delimiter=";")
	for line in list(class2featuremap)[1:]:
		idcl = line[0]
		idatt = line[2]
		if idatt not in feature2classes:
			feature2classes[idatt] = []
		feature2classes[idatt].append(idcl)
	
	feature2type = {}
	print "loading features"
	feature = csv.reader(open("pcs/eco5/eClass5_1_4_mm_de.csv", "r"), delimiter=";")
	for line in list(feature)[1:]:
		idatt = line[0]
		domain = []
		if idatt in feature2classes:
			domain = feature2classes[idatt]
		label = line[5]
		description = line[7]
		format = line[13]
		symbol = line[14] # e.g. mm for millimetres
		uom = line[15] # e.g. MMT for millimetres
		attribute_type = line[19] # e.g. direct (es erfolgt ein freier Eintrag) or indirect (Werte sind vorhanden)
		valency = line[20] # e.g. univalent (es wird genau ein Wert zugeordnet) or multivalent (Werte unbestimmter Anzahl werden zugeordnet)
		
		datatype = "string"
		object_type = "datatype"
		# http://www.heppnetz.de/projects/eclassowl/#gentax-properties
		if attribute_type == "indirect":
			object_type = "qualitative"
		elif format:
			if format[0] == "V": # boolean value
				object_type = "datatype"
				datatype = "boolean"
			elif "NR2" in format or "NE3" in format: # rational or exponential
				object_type = "quantitative"
				datatype = "float"
			elif "NR1" in format: # decimal
				object_type = "quantitative" # NR1 case has to be mapped manually, e.g. 10 properties ca. are datatype properties
				datatype = "integer"
			
		feature2type[idatt] = {}
		feature2type[idatt]["object_type"] = object_type
		feature2type[idatt]["datatype"] = datatype
		if len(domain) > 0:
			for d in domain:
				pappend(Property(d, idatt, label, description, prop_type=[object_type, datatype]))
		else:
			#print "could not determine domain for property", idatt, "- domain:", domain
			pappend(Property(None, idatt, label, description, prop_type=[object_type, datatype]))
		
	value2features = {}
	print "loading features2value mapping"
	feature2valuemap = csv.reader(open("pcs/eco5/eClass5_1_4_mm_we_de.csv", "r"), delimiter=";")
	for line in list(feature2valuemap)[1:]:
		idatt = line[0]
		idvl = line[1]
		if idvl not in value2features:
			value2features[idvl] = []
		value2features[idvl].append(idatt)
		
	# INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description="", inst_type=""):
	print "loading values"
	value = csv.reader(open("pcs/eco5/eClass5_1_4_we_de.csv", "r"), delimiter=";")
	for line in list(value)[1:]:
		idvl = line[0]
		label = line[5]
		description = line[6]
		if line[7]:
			description = line[7]
		if idvl in value2features:
			for feature in value2features[idvl]:
				if feature in feature2type:
					iappend(Individual(feature, idvl, label, description, [feature2type[feature]["object_type"], feature2type[feature]["datatype"]]))
				else:
					iappend(Individual(feature, idvl, label, description))


def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)