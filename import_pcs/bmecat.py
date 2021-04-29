#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
bmecat.py

BMECat catalog import module
- import the catalog structure only of a BMECat XML file

Created by Alex Stolz on 2011-04-13.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs
import xml.sax
import re

from util import * # imports also config, classes, rdflib, ...
import util

xml_file = "pcs/bmecat/AFB.xml"

catalog_group = Class(None, None)


def importData():
	"""Loading facility"""
	print "Step 1: Loading product catalog from %s" % __name__
	
	util.metadata = Ontology("BMECat", label="BME Catalog to OWL Converter", creator="Alex Stolz", contributor="Martin Hepp, Andreas Radinger")
	
	parser = xml.sax.make_parser()
	parser.setFeature("http://xml.org/sax/features/external-general-entities", False)
	parser.setContentHandler(EventHandler())
	parser.parse(open(xml_file, "r"))

def convert2OWL(element_type=None):
	"""Dummy function, see util.py"""
	util.convert2OWL(element_type)
	
def serialize(format="pretty-xml", filename=None):
	"""Dummy function, see util.py"""
	util.serialize(format, filename)

class Tag(): 
    """Class carrying tag metadata"""
    def __init__(self, stack, attrs, content):
        self.stack = stack
        self.attrs = attrs
        self.content = content

class EventHandler(xml.sax.ContentHandler):
	"""Event handler of SAX Parser"""
	def __init__(self):
		self.attrs = None
		self.stack = []
		self.catalog_close = False
    
	def startElement(self, name, attrs):
		"""This function gets called on every tag opening event"""
		self.attrs = attrs
		self.stack.append(name)
		self.content = ""

	def characters(self, ch):
		"""This function gets called for each literal content within a tag"""
		self.content = self.content + " ".join(ch.split())

	def endElement(self, name):
		"""This function gets called on every tag closing event"""
		# check if offer or businessentity tag has been closed -> if closed, store offer/business entity instance
		if name == "CATALOG_STRUCTURE":
			self.catalog_close = True

		if type(self.content) == unicode:
			self.content = self.content.encode("utf-8")
		tag = Tag(self.stack, self.attrs, xml.sax.saxutils.unescape(self.content, {"&szlig;":"ß", "&auml;":"ä", "&ouml;":"ö", "&uuml;":"ü", "&Auml;":"Ä", "&Ouml;":"Ö", "&Uuml;":"Ü"}))
		processData(tag, self.catalog_close)
		self.stack.pop()
		self.catalog_close = False

def processData(tag, catalog_close):
	"""Catch information on-the-fly and store as objects"""
	global catalog_group
	
	top = tag.stack[-1]
	subtop = None
	if len(tag.stack) > 1:
		subtop = tag.stack[-2]
		
	if catalog_close:
		cappend(catalog_group)
		catalog_group = Class(None, None)

	if subtop == "CATALOG_STRUCTURE" and catalog_group != None:
		if top == "GROUP_ID":
			if tag.content != "":
				catalog_group.id = "gid_"+re.sub(r"[^a-zA-Z0-9]", "", tag.content)
		elif top == "GROUP_NAME":
			catalog_group.label = tag.content
		elif top == "GROUP_DESCRIPTION":
			catalog_group.description = tag.content
		elif top == "PARENT_ID":
			if tag.content != "":
				catalog_group.parent_id = "gid_"+re.sub(r"[^a-zA-Z0-9]", "", tag.content)
