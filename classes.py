#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
classes.py

Classes, properties, and instances classes

Created by Alex Stolz on 2011-03-28.
Copyright (c) 2011 Ebusiness and Web Science Research Group. All rights reserved.
"""
class Ontology:
	def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
		self.title = title
		self.label = label
		self.description = description
		self.creator = creator
		self.contributor = contributor
		self.rights = rights
		self.subject = subject
		self.license = license
		self.version = version
		self.seeAlso = seeAlso

class Class:
	def __init__(self, parent_id, class_id, label="", description="", synonyms=""):
		self.parent_id = parent_id
		self.id = class_id
		self.label = label
		self.description = description
		self.synonyms = synonyms
		
class Property:
	def __init__(self, class_id, prop_id, label="", description="", prop_type=["qualitative", "string"]):
		self.domain = class_id
		self.id = prop_id
		self.label = label
		self.description = description
		self.type = prop_type # [<objecttype>, <datatype>], e.g. ["quantitative", "float"]
		
class Individual:
	def __init__(self, prop_id, inst_id, label="", description="", inst_type=["qualitative", "string"], uom=""):
		self.prop_id = prop_id
		self.id = inst_id
		self.label = label
		self.description = description
		self.type = inst_type # [<objecttype>, <datatype>], e.g. ["quantitative", "float"]
		self.uom = uom
		