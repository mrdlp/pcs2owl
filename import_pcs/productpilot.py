#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
unspsc.py

UNSPSC import module
- question regarding licenses etc.

Created by Alex Stolz on 2011-04-28.
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
	util.metadata = Ontology("Productpilot", label="Productpilot Classification", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	classes = csv.reader(open("pcs/productpilot/productpilot.csv", "r"), delimiter=";")
	parents = []
	idf = None
	for line in list(classes)[1:]:
		if line[0] != idf:
			# process classes with information from last loops
			# id label_de parent_id label_en
			if len(parents) > 1:
				cappend(Class(parents, idf, {"de":label_de, "en":label_en}))
			elif idf: # idf in first iteration = None
				cappend(Class(parent_idf, idf, {"de":label_de, "en":label_en}))
			
			# prepare for next loop iteration
			label_de = line[1]
			label_en = line[3]
			idf = line[0]
			parents = []
			
		parent_idf = line[2]
		parents.append(parent_idf)
			
	# last line will be appended here
	if len(parents) > 0:
		cappend(Class(parents, idf, {"de":label_de, "en":label_en}))
		parents = []
	else:
		cappend(Class(parent_idf, idf, {"de":label_de, "en":label_en}))

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)