#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
proficlass.py

proficl@ss import module

Created by Alex Stolz on 2011-04-06.
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
	util.metadata = Ontology("proficlass", label="proficlass 4.0", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	# class synonyms
	synonyms = {}
	print "loading class synonyms"
	synonym_de = csv.reader(open("pcs/proficlass/Schlagworte.csv", "r"), delimiter=";")
	for line in list(synonym_de)[1:]:
		idsyn = line[0]
		desc = line[1]
		synonyms[idsyn] = desc
		
	names = {}
	print "loading synonym2class mappings"
	synonym2class = csv.reader(open("pcs/proficlass/KlassenSchlagworte_rel.csv", "r"), delimiter=";")
	for line in list(synonym2class)[1:]:
		idcl = line[1]
		idsyn = line[2]
		if not idcl in names:
			names[idcl] = []
		if idsyn in synonyms:
			names[idcl].append(synonyms[idsyn])
	
	codes = {}
	print "loading classes"
	artclass = csv.reader(open("pcs/proficlass/Klassen.csv", "r"), delimiter=";")
	for line in list(artclass)[1:]:
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		idcl = line[0]
		parent = line[1]
		label = line[2]
		if idcl in names:
			desc = names[idcl]
			desc.append(label)
		else:
			desc = label
		cappend(Class(parent, idcl, label, synonyms={"de":desc}))
	
	# feature
	# PROPERTY: def __init__(self, class_id, prop_id, label="", description="", prop_type=["qualitative", "string"]):
	features = {}
	print "loading features"
	feature = csv.reader(open("pcs/proficlass/Merkmale.csv", "r"), delimiter=";")
	for line in list(feature)[1:]:
		idatt = line[0]
		desc = line[1]
		datatype = line[2]
		features[idatt] = {"desc":desc, "type":datatype}
	
	primkey_features = {}
	feature2classes = {}
	print "loading feature2classes mapping"
	class2featuremap = csv.reader(open("pcs/proficlass/KlassenMerkmale_rel.csv", "r"), delimiter=";")
	for line in list(class2featuremap)[1:]:
		idcl = line[1]
		idatt = line[2]
		uom = line[3]
		primkey_features[line[0]] = idatt
		datatype = features[idatt]["type"]
		desc = features[idatt]["desc"]
		
		ptype = ["datatype", "string"] # default
		# [<objecttype>, <datatype>], e.g. ["quantitative", "float"]
		if datatype == "alphanumerisch": # alphanumerical
			ptype = ["qualitative", "string"]
		elif datatype == "numerisch": # numerical
			if uom != "": # has UOM
				ptype = ["quantitative", "float"]
			else: # has no UOM
				ptype = ["datatype", "float"]
		elif datatype == "logisch": # logical
			ptype = ["datatype", "boolean"]
			
		pappend(Property(idcl, idatt, desc, desc, ptype))
	
	# INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description=""):
	value2feature = {}
	print "loading feature2value mapping"
	artclassfeaturevaluemap = csv.reader(open("pcs/proficlass/KlassenMerkmaleWerte_rel.csv", "r"), delimiter=";")
	for line in list(artclassfeaturevaluemap)[1:]:
		idatt = primkey_features[line[1]]
		idval = line[2]
		value2feature[idval] = idatt
	
	print "loading values"
	values = csv.reader(open("pcs/proficlass/Werte.csv", "r"), delimiter=";")
	for line in list(values)[1:]:
		idval = line[0]
		desc = line[1]
		if idval in value2feature:
			iappend(Individual(value2feature[idval], idval, desc))
		else:
			iappend(Individual(None, idval, desc))
	

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)