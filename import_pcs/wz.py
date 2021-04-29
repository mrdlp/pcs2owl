#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wz.py

WZ2008 import module
- http://www.destatis.de/jetspeed/portal/cms/Sites/destatis/Internet/DE/Content/Klassifikationen/GueterWirtschaftklassifikationen/Content75/KlassifikationWZ08,templateId=renderPrint.psml

Created by Alex Stolz on 2011-03-25.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs
import xlrd

from util import * # imports also config, classes, rdflib, ...
import util

def importData():
	"""Loading facility"""
	print "Step 1: Loading PCS from %s" % __name__
	
	# ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
	util.metadata = Ontology("WZ", label="WZ 2008", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	book = xlrd.open_workbook("pcs/wz/wz2008.xls")
	book_en = xlrd.open_workbook("pcs/wz/wz2008en.xls")
	
	sheet = book.sheet_by_name("WZ 2008 - Gliederung")
	sheet_en = book_en.sheet_by_name("WZ 2008")
	header = []
	descriptions = []
	codes = []
	section = ""
	dappend = descriptions.append
	coappend = codes.append
	for i in range(0, sheet.nrows):
		dappend({})
		for j in range(0, sheet.ncols):
			if i == 0: # header
				header.append(sheet.cell_value(i, j))
			else:
				if j == 1: # code
					code = sheet.cell_value(i,j)
					if len(code) == 1: # a letter
						section = code
					coappend(section+code) # e.g. A01
				elif j == 2:
					descriptions[i]["de"] = sheet.cell_value(i,j)
					descriptions[i]["en"] = sheet_en.cell_value(i,j)
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		if codes and len(codes[i-1]) > 0:
			section = codes[i-1][0]
			idf = codes[i-1][1:] # i-1? yes, in i=0 we didn't attach to codes list
			parent_idf = None
			if len(idf) > 2: # something starting with two numbers at least
				for k in range(1, len(idf)-2): # go upwards until 01, if code/idf is 01.11.12 for example
					if parent_idf and section+parent_idf in codes: # saw parent id already
						break
					else:
						parent_idf = idf[:-k].strip(".")
			elif len(idf) == 1:
				pass # do nothing, idf has no parents
			else:
				parent_idf = section
			print "parent:",parent_idf,"child:", idf
			cappend(Class(parent_idf, idf, descriptions[i], descriptions[i][lang]))
	
	book_en.unload_sheet("WZ 2008")
	book.unload_sheet("WZ 2008 - Gliederung")
	

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)