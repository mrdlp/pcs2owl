#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cpa.py

NACE_Rev2-CPA2008 import module
- http://circa.europa.eu/irc/dsis/nacecpacon/info/data/en/2007%20introduction.htm
- http://epp.eurostat.ec.europa.eu/statistics_explained/index.php/Glossary:CPA
- http://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=CPA_2008&StrLanguageCode=EN&IntPcKey=&StrLayoutCode=
- exported classification from .mdb file into .xls

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
	util.metadata = Ontology(title="CPA", label="NACE Rev 2 - CPA 2008", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	book = xlrd.open_workbook("pcs/cpa/cpa2008.xls")
	
	sheet = book.sheet_by_name("Classifications___CPA_2008___st")
	header = []
	descriptions = []
	codes = []
	for i in range(0, sheet.nrows):
		descriptions.append({})
		for j in range(0, sheet.ncols):
			if i == 0: # header
				header.append(sheet.cell_value(i, j))
			else:
				if j == 1: # code
					code = sheet.cell_value(i,j)
					codes.append(code)
				elif "DESC" in header[j]: # CPA_2008_DESCRIPTION, DE_DESC, FR_DESC, ...
					lang_code = header[j][:2].lower()
					if lang_code == "cp" and j == 5: # column for english description
						lang_code = "en"
					descriptions[i][lang_code] = sheet.cell_value(i,j)
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		if codes:
			idf = codes[i-1] # i-1? yes, in i=0 we didn't attach to codes list
			parent_idf = None
			if len(idf) > 2: # something starting with two numbers at least
				for k in range(1, len(idf)-2): # go upwards until 01, if code/idf is 01.11.12 for example
					if parent_idf and parent_idf in codes: # saw parent id already
						break
					else:
						parent_idf = idf[:-k].strip(".")
			elif len(idf) == 1:
				pass # do nothing, idf has no parents
			else:
				parent_idf = sheet.cell_value(i, 2) # Section_CPA column
			#print parent_idf, idf
			cappend(Class(parent_idf, idf, descriptions[i], descriptions[i][lang]))

	book.unload_sheet("Classifications___CPA_2008___st")
	

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)