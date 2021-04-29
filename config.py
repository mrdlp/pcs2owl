#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
config.py

Configuration module

Created by Alex Stolz on 2011-03-28.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
from rdflib import *
import os
import sys

ns = "google" #"proficlass" # namespace prefix name of local data
if len(sys.argv) > 1:
	ns = sys.argv[1]
#lang = "de" # global language
#include_annotationprops = False # include recommendation annotation properties such as recommendedProperty and recommendedValue... if True, then the whole generation process will take much longer
#dump_mode = True # if True, create one single dump file, else create 1 file for every element (class, category, property, ...)
#base_uri = "http://www.intelligent-match.de/eco5/" # deployment uri... decide whether to use hash URIs or slash URIs, e.g. http://www.example.com/pcs# vs. http://www.example.com/pcs/
#create_dump = False # if True, write also a dump file besides the single files (has an effect only if dump_mode = False)
#out_dir = "output" # local output directory
#hashcode_select = "cpv" # use hash coded ids for classes (c), properties (p) and values (v)? allowed values are e.g. combinations as "c", "cv", "cpv", ...

pre_pcs = {
	"cpa": {
		"lang":"en",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/cpa/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"cpv": {
		"lang":"en",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/cpv/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"eco5": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/eco5/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"eco6": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/eco6/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"etim": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/etim/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"gpc": {
		"lang":"en",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/gpc/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"proficlass": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/proficlass/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"wz": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/wz/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	"google": {
	    "lang":"en",
		"include_annotationprops": True,
		"dump_mode": True,
		"base_uri": "http://www.intelligent-match.de/google/",
		"create_dump": True,
		"out_dir": "output/product_classification_standards",
		"hashcode_select": ""
	},
	# non pcs
	"productpilot": {
		"lang":"en",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/productpilot/",
		"create_dump": True,
		"out_dir": "output/productpilot",
		"hashcode_select": ""
	},
	"bmecat": {
		"lang":"de",
		"include_annotationprops": True,
		"dump_mode": False,
		"base_uri": "http://www.intelligent-match.de/bmecat/AFB/",
		"create_dump": True,
		"out_dir": "output/bmecat_sample",
		"hashcode_select": ""
	}
}

for key, value in pre_pcs[ns].items():
	globals()[key] = value

ontologies = {
	ns: base_uri,
	"gr": "http://purl.org/goodrelations/v1#",
	"owl": "http://www.w3.org/2002/07/owl#",
	"dc": "http://purl.org/dc/elements/1.1/",
	"skos": "http://www.w3.org/2004/02/skos/core#",
	"dcterms": "http://purl.org/dc/terms/",
	"rdfs": "http://www.w3.org/2000/01/rdf-schema#",
	"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}


if not dump_mode:
	out_dir = "%s/%s" % (out_dir, ns)
	
try:
	if not os.path.exists("%s" % out_dir):
		os.makedirs("%s" % out_dir)
except OSError, e:
	print e
	
if not dump_mode:
	sem_sitemap = open("%s/sitemap.xml" % out_dir, "w")
	
metadata = ""
classes = []
properties = []
individuals = []
params = {}
recommended_properties = {}
recommended_values = {}

g = Graph()
for k, v in ontologies.items():
	g.bind(k, v)
	kupper = k.upper()
	globals()[kupper] = Namespace(v)
	params[k] = globals()[kupper]
#g.bind(None, ontologies[ns])
	
SELF = globals()[ns.upper()]
