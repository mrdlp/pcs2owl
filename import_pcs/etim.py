#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
etim.py

ETIM 4.0 import module
- http://www.etim.de/65.0.html

Created by Alex Stolz on 2011-03-25.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs
import csv
#import sys 
#reload(sys) 
#sys.setdefaultencoding("utf-8")

from util import * # imports also config, classes, rdflib, ...
import util

def importData():
	"""Loading facility"""
	print "Step 1: Loading PCS from %s" % __name__
	
	# ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
	util.metadata = Ontology("ETIM", label="ETIM Klassifikationsmodell 4.0", description="Das ETIM Klassifikationsmodell definiert Produktklassen und die technischen Merkmale, die bei der Einklassifizierung eines Produkts in eine Produktklasse anzugeben sind.", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0", license="Creative Commons 3.0")
	
	group = csv.reader(open("pcs/etim/ETIMARTGROUP.csv", "r"), delimiter=";")
	for line in list(group)[1:]:
		cappend(Class("", line[0], line[1]))
		
	# class synonyms
	names = {}
	synonym_de = csv.reader(open("pcs/etim/ETIMSYNONYM_DE.csv", "r"), delimiter=";")
	for line in list(synonym_de)[1:]:
		if not line[0] in names:
			names[line[0]] = []
		names[line[0]].append(line[1])
	
	artclass = csv.reader(open("pcs/etim/ETIMARTCLASS.csv", "r"), delimiter=";")
	#artclass = open("pcs/etim/ETIMARTCLASS.csv", "r")
	for line in list(artclass)[1:]:
		# CLASS: def __init__(self, parent_id, class_id, label="", description="", synonyms=""):
		names[line[0]].append(line[2])
		cappend(Class(line[1], line[0], line[2], synonyms={"de":names[line[0]]}))
		
	# feature
	# PROPERTY: def __init__(self, class_id, prop_id, label="", description=""):
	features = {}
	feature = csv.reader(open("pcs/etim/ETIMFEATURE.csv", "r"), delimiter=";")
	for line in list(feature)[1:]:
		features[line[0]] = line[1]
			
	featuremap = {}
	artclassfeaturemap = csv.reader(open("pcs/etim/ETIMARTCLASSFEATUREMAP.csv", "r"), delimiter=";")
	for line in list(artclassfeaturemap)[1:]:
		featuremap[line[0]] = line[2]
		ptype = ["datatype", "string"] # default
		# [<objecttype>, <datatype>], e.g. ["quantitative", "float"]
		if line[3] == "R": # range
			ptype = ["quantitative", "float"]
		elif line[3] == "A": # alphanumerical
			ptype = ["qualitative", "string"]
		elif line[3] == "N": # numerical
			if line[4] != "": # has UOM
				ptype = ["quantitative", "float"]
			else: # has no UOM
				ptype = ["datatype", "float"]
		elif line[3] == "L": # logical
			ptype = ["datatype", "boolean"]
		pappend(Property(line[1], line[2], features[line[2]], features[line[2]], ptype))
		
	valuemap = {}
	etimvalue = csv.reader(open("pcs/etim/ETIMVALUE.csv", "r"), delimiter=";")
	for line in list(etimvalue)[1:]:
		valuemap[line[0]] = line[1]
		
	# INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description=""):
	artclassfeaturevaluemap = csv.reader(open("pcs/etim/ETIMARTCLASSFEATUREVALUEMAP.csv", "r"), delimiter=";")
	for line in list(artclassfeaturevaluemap)[1:]:
		iappend(Individual(featuremap[line[1]], line[2], valuemap[line[2]]))

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)