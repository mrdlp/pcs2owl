#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
cpv.py

CPV import module
- http://simap.europa.eu/codes-and-nomenclatures/codes-cpv/codes-cpv_en.htm

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
	util.metadata = Ontology("CPV", label="Common Procurement Vocabulary", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger", version="1.0")
	
	book = xlrd.open_workbook("pcs/cpv/cpv_2008.xls")
	
	print "loading classes"
	# "35"000000-4 -> Division
	# 35"1"00000-5 -> Group
	# 351"1"0000-8 -> Class
	# 3511"2"000-2 -> Category
	# 35112"100"-3 -> Subcategory
	sheet = book.sheet_by_name("CPV codes")
	header = []
	descriptions = []
	codes = []
	codes_rstrip = []
	parents = set()
	for i in range(0, sheet.nrows):
		descriptions.append({})
		for j in range(0, sheet.ncols):
			if i == 0: # header
				header.append(sheet.cell_value(i, j))
			else:
				if j == 0: # code
					code = sheet.cell_value(i,j)
					codes.append(code)
					codes_rstrip.append(code[:-2])
				else:
					descriptions[i][header[j].lower()] = sheet.cell_value(i,j)
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		if codes:
			code = codes[i-1] # i-1? yes, in i=0 we didn't attach to codes list
			idf = code[:-2] # with trailing zeros
			idf_rstrip = idf.rstrip("0") # without trailing zeros
			
			parent_idf = None
			category = idf_rstrip[:6]
			if len(category) > 2: # 123 (group) to 123456 (subcategory)
				for k in range(1, len(category)-2): # go upwards until 12 (division)
					if parent_idf and parent_idf in codes_rstrip:
						break
					else:
						# for debugging
						#if k>1:
						#	parents.add(parent_idf)
						parent_idf = category[:-k]+"0"*(8-len(category[:-k]))
			cappend(Class(parent_idf, idf, descriptions[i], descriptions[i][lang]))
	# for debugging
	#print parents
	book.unload_sheet("CPV codes")
	
	print "loading supplementary categories"
	sheet = book.sheet_by_name("Supplementary categories")
	section = ""
	group = ""
	for i in range(1, sheet.nrows):
		row = sheet.cell_value(i,0)
		a, b = row.split(":")
		if "Section" in a:
			section = a[-1]
			cappend(Class("", section, a, b.strip()))
		elif "Group" in a:
			group = a[-1]
			cappend(Class(section, section+group, a, b.strip()))
			
	book.unload_sheet("Supplementary categories")
	
	print "loading supplementary codes"
	# "A"A01-1 -> Section
	# A"B"01-1 -> Group
	# AB"01"-1 -> Attribute definition
	
	# Example: A procurement entity interested in buying passenger car will choose the following codes to describe its object:
	# - 34110000-1 Passenger cars
	# - MB02-8 Right-hand-drive
	# - CA36-8 Euro 5 (fuel)
	sheet = book.sheet_by_name("Supplementary codes")
	header = []
	descriptions = []
	codes = []
	codes_rstrip = []
	parents = set()
	for i in range(0, sheet.nrows):
		descriptions.append({})
		for j in range(0, sheet.ncols):
			if i == 0: # header
				header.append(sheet.cell_value(i, j))
				#if j > 0:
					#descriptions[header[j].lower()] = []
			else:
				if j == 0: # code
					code = sheet.cell_value(i,j)
					codes.append(code)
					codes_rstrip.append(code[:-2])
				else:
					descriptions[i][header[j].lower()] = sheet.cell_value(i,j)
		# CLASS: def __init__(self, parent_id, class_id, label="", description=""):
		if codes:
			code = codes[i-1] # i-1? yes, in i=0 we didn't attach to codes list
			idf = code[:-2] # with trailing zeros
			parent_idf = idf[:2] # section A, group A = AA
			cappend(Class(parent_idf, idf, descriptions[i], descriptions[i][lang]))	
	
	book.unload_sheet("Supplementary codes")
	

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)