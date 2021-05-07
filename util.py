#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
util.py

Helper functions like hash encoding, etc.

Created by Alex Stolz on 2011-03-25.
Copyright (c) 2011 Ebusiness and Web Science Research Group. All rights reserved.
"""
import rdflib
from rdflib.collection import Collection
from jinja2 import *
import codecs
import re
import hashlib

from config import *
import config
from classes import *

loader = FileSystemLoader(".")
env = Environment(loader=loader)
template_ontology = env.get_template("templates/ontology.html")
template_class = env.get_template("templates/class.html")
template_instance = env.get_template("templates/instance.html")
template_property = env.get_template("templates/property.html")

def encodeId(idf):
	"""Hash encoding of class IDs for protecting IPR (eClass does not want to reveal original IDs in open version)"""
	return hashlib.sha1(idf).hexdigest()
	
def cappend(obj):
	"""Append class objects to classes list"""
	if "c" in hashcode_select:
		if obj.id != None:
			obj.id = encodeId(obj.id)
		if obj.parent_id != None:
			obj.parent_id = encodeId(obj.parent_id)
	classes.append(obj)
	
def pappend(obj):
	"""Append property objects to properties list"""
	if "p" in hashcode_select:
		if obj.id != None:
			obj.id = encodeId(obj.id)
		if "c" in hashcode_select:
			if obj.domain != None:
				obj.domain = encodeId(obj.domain)
	properties.append(obj)
	cidf = "C_%s-gen" % obj.domain
	pidf = "P_%s" % obj.id
	if not cidf in recommended_properties:
		recommended_properties[cidf] = []
	recommended_properties[cidf].append(pidf)
	
def iappend(obj):
	"""Append instance objects to instances list"""
	if "v" in hashcode_select:
		if obj.id != None:
			obj.id = encodeId(obj.id)
		if "p" in hashcode_select:
			if obj.prop_id != None:
				obj.prop_id = encodeId(obj.prop_id)
	individuals.append(obj)
	pidf = "P_%s" % obj.prop_id
	iidf = "V_%s" % obj.id
	if not pidf in recommended_values:
		recommended_values[pidf] = []
	recommended_values[pidf].append(iidf)
	
def URIRef(elem, filename=""):
	"""Combine elem of URIRef with ontology namespace and optional filename (e.g. if you want distinguish between classes.rdf, instances.rdf and properties.rdf)"""
	return rdflib.URIRef(ontologies[config.ns]+filename+elem)
	
def Literal(elem):
	"""Overwrites RDFLib Literal and supports stripping of spaces in addition"""
	return rdflib.Literal(elem.strip())
	
def addLinks(html):
	"""Adds HTML links to known CURIEs in the final HTML.
	
	Arguments:
	html -- Unicode string with HTML content
	"""
	r_utf8 = re.sub("([^(>|\"|=)][ ]*)(http://(\w|\.|/|#|-)+(\w|/))", "\\1<a href=\"\\2\">\\2</a>", html)
	#r_utf8 = re.sub("(Examples?:)", "<span style=\"text-decoration: underline\">\\1</span>", r_utf8)
	
	#for key, value in ontologies.items():
	#	pattern = "([^(>|\"|=)][ ]*)(%s:)((\w|\.|/|#|-)+(\w|/))" % key
	#	replacement = "\\1<a href=\"%s\\3\">\\2\\3</a>" % value
	#	r_utf8 = re.sub(pattern, replacement, r_utf8)
	#r_utf8 = re.sub("(DEPRECATED)", "<span class=\"deprecated\">\\1</span>", r_utf8)
	#r_utf8 = re.sub("id=\"([0-9]{1})", "id=\"_\\1", r_utf8) # fix xhtml validation errors for URIs starting with a digit (4WD, 1GLL, 1LTR)
	#r_utf8 = re.sub("href=\"#([0-9]{1})", "href=\"#_\\1", r_utf8) # fix internal links accordingly
	return r_utf8
	
def getAllTypesOfElement(graph, e):
	'''Get a list of all types the given element belongs to.
	
	Arguments:
	g -- rdflib.ConjunctiveGraph
	e -- element
	'''
	types = []
	for t in graph.objects(e, RDF.type):
		types.append(str(t))
	return types

def prettyList(rod_list):
	'''Bring the passed list to a suitable format and return the formatted string with anchor links.
	
	Arguments:
	rod_list -- range or domain list (any type of c, dp, op, ap or i)
	'''
	if not rod_list:
		return ""
	pretty_format = "<span class=\"item_list\">"
	if type(rod_list) is list:
		rod_list.sort() # sort the list alphabetically
		for item in rod_list:
			if item[:len(base_uri)] == base_uri: # VOCAB link
				# navigation in html document, if VOCAB ontology base uri is found
				pretty_format += " <a href=\"%s\">%s:%s</a>" % (item[len(base_uri):], config.ns, item[len(base_uri):])
			else:
				pretty_format += " <a href=\"%s\">%s</a>" % (item, item)
	else:
		if rod_list[:len(base_uri)] == base_uri: # VOCAB link
			# navigation in html document, if VOCAB ontology base uri is found
			pretty_format += " <a href=\"%s\">%s:%s</a>" % (rod_list[len(base_uri):], config.ns, rod_list[len(base_uri):])
		else:
			pretty_format += " <a href=\"%s\">%s</a>" % (rod_list, rod_list)
	pretty_format += "</span>"
	return pretty_format
	
def printTypes(types, prefix="owl"):
	'''Print the types an element belongs to.
	
	Arguments:
	types -- types of an element (can be of SPIN...)
	'''
	if prefix == None:
		return types
	text = ""
	if type(types) == list:
		types.sort()
		i = 0
		for t in types:
			if i==0:
				text += "<a href=\"%s\">%s:%s</a>" % (t, prefix, t[len(globals()[prefix.upper()]):])
			else:
				text += ", <a href=\"%s\">%s:%s</a>" % (t, prefix, t[len(globals()[prefix.upper()]):])
			i += 1
	elif type(types) in [URIRef, str]:
		text = "<a href=\"%s\">%s:%s</a>" % (types, prefix, types[len(globals()[prefix.upper()]):])
	return text

def getDomain(graph, subject):
	'''Function that fetches domain items from a collection (here unionOf) and returns them as list of URIRefs or single URIRef.
	'''
	dom = graph.value(subject, RDFS.domain)
	
	if type(dom) is not URIRef:
		dom_list = []
		for dom_outer_class in graph.objects(subject, RDFS.domain): # get OWL:Class
			if type(dom_outer_class) is BNode:
				#print graph.value(dom_outer_class, RDF.type) # should output OWL:Class
				for dom_collection in graph.objects(dom_outer_class, OWL.unionOf):
					domains = list(graph.items(dom_collection))
					for d in domains:
						#print d # should output the domain URIs
						d_uri = str(d)
						#if d_uri[:d_uri.find("#")+1] == base_uri:
						#	d_idf = d_uri[d_uri.find("#")+1:] # navigation in html document, if VOCAB ontology base uri is found
						dom_list.append(d_uri)
		dom = dom_list
	
	if type(dom) is not list:
		dom = [str(dom)]
	
	# fetch all domains from superclasses as well ... slows down application
	for d in dom:
		subclasses = graph.subjects(RDFS.subClassOf, URIRef(d))
		for sc in subclasses:
			dom.append(str(sc))
	
	return dom

def serializeHTML(filename=None, graph=None):
	"""Serialize contents of graph as HTML"""
	global g
	lg = None
	if graph:
		lg = graph # graph was passed as parameter
	else:
		lg = g # global g
	
	if not filename: # serialize ontology info only as html
		idf = ""
		params_local = {
			"title":metadata.title, "label":metadata.label, "description":metadata.description,
			"creator":metadata.creator, "contributor":metadata.contributor, "rights":metadata.rights,
			"subject":metadata.subject, "license":metadata.license, "version":metadata.version,
			"seeAlso":metadata.seeAlso, "ns":config.ns, "idf":idf, "idref":str(URIRef(idf)),
			"type":"<a href=\"%s\">%s</a>" % (OWL.Ontology, "owl:Ontology")
		}
		params.update(params_local)
		
		html_filepath = "%s/%s.html" % (out_dir, "O_%s" % config.ns)
		html = codecs.open(html_filepath, encoding="utf-8", mode="w")
		s = template_ontology.render(params)
		html.write(addLinks(s))
		html.close()
	
	if filename and lg and len(filename) > 4: # filename is <something>.rdf, so at least 4 characters long
		idf = filename[:-4]
		html_filepath = "%s/%s.html" % (out_dir, idf)
		title = metadata.title
		
		for c in lg.subjects(RDF.type, OWL.Class):
			labels = set(lg.objects(c, RDFS.label))
			descriptions = set(lg.objects(c, RDFS.comment))
			synonyms = list(lg.objects(c, SKOS.altLabel))
			subclassof = list(lg.objects(c, RDFS.subClassOf))
			recommendedProperties = list(lg.objects(c, SELF.recommendedProperty))
			hierarchycode = lg.value(c, SELF.hierarchyCode)
			
			if labels == descriptions:
				descriptions = set()
			description = ""
			toremove = []
			for d in descriptions:
				if d.language == "en":
					description = d
					toremove.append(description)
				elif d.language == "de":
					description = d
					toremove.append(description)
			for r in toremove:
				descriptions.remove(r)

			params_local = {
				"ns":config.ns, "base_uri":base_uri, "idref":str(c),
				"title":title, "hierarchycode":hierarchycode, "types":printTypes(getAllTypesOfElement(lg, c)),
				"idf":idf, "description":description,
				"labels":sorted(labels, key=lambda l: l.language), "descriptions":sorted(descriptions, key=lambda d: d.language), "synonyms":sorted(synonyms),
				"recommended":prettyList(recommendedProperties), "subclassof":prettyList(subclassof)
			}
			params.update(params_local)
			
			html = codecs.open(html_filepath, encoding="utf-8", mode="w")
			s = template_class.render(params)
			html.write(addLinks(s))
			html.close()
		
		for t in [OWL.ObjectProperty, OWL.DatatypeProperty]:
			for p in lg.subjects(RDF.type, t):
				labels = set(lg.objects(p, RDFS.label))
				descriptions = set(lg.objects(p, RDFS.comment))
				domains = list(lg.objects(p, RDFS.domain))
				rangeval = lg.value(p, RDFS.range)
				recommendedValues = list(lg.objects(p, SELF.recommendedValue))
				subpropertyof = list(lg.objects(p, RDFS.subPropertyOf))
				
				if labels == descriptions:
					descriptions = set()
				description = ""
				toremove = []
				for d in descriptions:
					if d.language == "en":
						description = d
						toremove.append(description)
					elif d.language == "de":
						description = d
						toremove.append(description)
				for r in toremove:
					descriptions.remove(r)
						
				params_local = {
					"ns":config.ns, "base_uri":base_uri, "idref":str(p),
					"title":title, "types":printTypes(getAllTypesOfElement(lg, p)),
					"idf":idf, "description":description,
					"labels":sorted(labels, key=lambda l: l.language), "descriptions":sorted(descriptions, key=lambda d: d.language),
					"recommended":prettyList(recommendedValues), "subpropertyof":prettyList(subpropertyof),
					"domain":prettyList(getDomain(lg, p)), "range":rangeval
				}
				params.update(params_local)

				html = codecs.open(html_filepath, encoding="utf-8", mode="w")
				s = template_property.render(params)
				html.write(addLinks(s))
				html.close()
				
		for t in [GR.QualitativeValue, GR.QuantitativeValue]:
			for i in lg.subjects(RDF.type, t):
				labels = set(lg.objects(i, RDFS.label))
				descriptions = set(lg.objects(i, RDFS.comment))
				uom = lg.value(i, GR.hasUnitOfMeasurement)
				
				if labels == descriptions:
					descriptions = set()
				description = ""
				toremove = []
				for d in descriptions:
					if d.language == "en":
						description = d
						toremove.append(description)
					elif d.language == "de":
						description = d
						toremove.append(description)
				for r in toremove:
					descriptions.remove(r)
					
				params_local = {
					"ns":config.ns, "idref":str(i),
					"title":title, "types":printTypes(getAllTypesOfElement(lg, i)),
					"idf":idf, "description":description, "uom":uom,
					"labels":sorted(labels, key=lambda l: l.language), "descriptions":sorted(descriptions, key=lambda d: d.language)
				}
				params.update(params_local)

				html = codecs.open(html_filepath, encoding="utf-8", mode="w")
				s = template_instance.render(params)
				html.write(addLinks(s))
				html.close()
				
	
def triplifyResource(subject, rel_type, resource, text="%s"):
	"""Create triples for unknown resources (either of types string, dict or list)"""
	if type(resource) == dict:
		for k, v in resource.items():
			if type(v) == list:
				for i in v:
					triple(g, subject, rel_type, Literal(text % i), language=k)
			else:
				triple(g, subject, rel_type, Literal(text % v), language=k)
	elif type(resource) == list:
		for i in resource:
			triple(g, subject, rel_type, Literal(text % i), language=lang)
	elif type(resource) in [str, unicode]:
		triple(g, subject, rel_type, Literal(text % resource), language=lang)
	else:
		print "WARNING: don't know what to do with (type:%s) %s" % (type(resource), resource)

def triple(g, subject, predicate, object, datatype=None, language=None):
	"""Create a triple in graph g"""
	if type(object) == rdflib.Literal:
		# return if content is empty
		if object.title() == "":
			return False
		# check if language tag is given
		if language != None:
			object._language = language
		# if no language tag is given, check if datatype is available
		elif datatype != None:
			object._datatype = datatype
	elif type(object) == rdflib.URIRef:
		if object.title() == "":
			return False
	# create triple in graph g
	g.add((subject, predicate, object))
	return True

def graphFlush(format="pretty-xml", filename=None):
	"""Serialize graph if items are available and create a new instance"""
	global g
	if isinstance(g, Graph) and len(g) > 0:
		serialize(format, filename)
		serializeHTML(filename)
		# write semantic sitemap
		dump = ""
		if create_dump:
			dump = """
        <sc:dataDumpLocation>%s%s.rdf</sc:dataDumpLocation>""" % (base_uri, config.ns)
		first2letters = filename[:2]
		idf = filename[2:-4]
		label = ""
		if first2letters == "O_":
			label = "Ontology %s" % idf
		elif first2letters == "C_":
			label = "Class %s" % idf
		elif first2letters == "P_":
			label = "Property %s" % idf
		elif first2letters == "V_":
			label = "Value %s" % idf
		else:
			label = filename
		sem_sitemap.write("""	<sc:dataset>
        <sc:datasetLabel>%(label)s</sc:datasetLabel>
        <sc:datasetURI>%(base_uri)s%(filename)s</sc:datasetURI>
        <sc:linkedDataPrefix slicing="subject-object">%(base_uri)s</sc:linkedDataPrefix>
        <sc:sampleURI>%(base_uri)s%(filename)s</sc:sampleURI>%(dump)s
        <changefreq>monthly</changefreq>
    </sc:dataset>
""" % ({"label":label, "base_uri":base_uri, "filename":filename, "dump":dump}))
	
	g = Graph()
	for k, v in ontologies.items():
		g.bind(k, v)

def loadGraph(filename):
	"""Load persistent graph into memory"""
	global g
	f = open("%s/%s" % (out_dir, filename), "r")
	data = f.read()
	if data:
		g.parse(data=data, format="xml")	

def gentax(classes):
	"""GenTax approach"""
	global g
	for c in classes:
		if not c.id: # skip empty ids
			print "\t\tskipped empty id"
			continue
		# tax
		idf = "C_"+c.id+"-tax"
		idref_tax = URIRef(idf)
		triple(g, idref_tax, RDF.type, OWL.Class)
		if c.parent_id:
			pid = c.parent_id
			if type(pid) == list:
				for parent in pid:
					triple(g, idref_tax, RDFS.subClassOf, URIRef("C_%s-tax" % parent))
			else:
				triple(g, idref_tax, RDFS.subClassOf, URIRef("C_%s-tax" % pid))
		label = c.label
		description = c.label
		if c.description:
			description = c.description
		triplifyResource(idref_tax, RDFS.label, label, "%s (Taxonomy Concept: Anything that may be an instance of this category in any context)")
		triplifyResource(idref_tax, RDFS.comment, description, "This class subsumes everything that is a member of the following category of products or services in any relevant context: %s. It includes both related types of goods (e.g. accessories, supplies, ...) and items that are no actual goods of this kind but related to the respective category (e.g. expenses reflecting such goods).")
		synonyms = c.synonyms
		if len(synonyms) > 0: # make sure we stay in OWL DL
			triple(g, SKOS.altLabel, RDF.type, OWL.AnnotationProperty)
		triplifyResource(idref_tax, SKOS.altLabel, synonyms)
		triple(g, idref_tax, SELF.hierarchyCode, Literal(c.id))
		triple(g, idref_tax, RDFS.isDefinedBy, URIRef(""))
		# serialize and reset
		if not config.dump_mode:
			graphFlush("pretty-xml", "%s.rdf" % idf)
		# gen
		if len(synonyms) > 0: # make sure we stay in OWL DL
			triple(g, SKOS.altLabel, RDF.type, OWL.AnnotationProperty)
		idf = "C_"+c.id+"-gen"
		idref_gen = URIRef(idf)
		triple(g, idref_gen, RDF.type, OWL.Class)
		triple(g, idref_gen, RDFS.subClassOf, GR.ProductOrService)
		triple(g, idref_gen, RDFS.subClassOf, idref_tax)
		triplifyResource(idref_gen, RDFS.label, label, "%s (Generic Concept: This type of goods)")
		triplifyResource(idref_gen, RDFS.comment, description, "This class subsumes all actual instances of the following type of goods and true specializations: %s.")
		triplifyResource(idref_gen, SKOS.altLabel, synonyms)
		triple(g, idref_gen, RDFS.isDefinedBy, URIRef(""))
		
		# attach annotations if required
		if include_annotationprops and idf in recommended_properties:
			for pidf in set(recommended_properties[idf]):
				triple(g, idref_gen, SELF.recommendedProperty, URIRef(pidf))
					
		# serialize and reset
		if not config.dump_mode:
			graphFlush("pretty-xml", "%s.rdf" % idf)

def convert2OWL(element_type=None):
	"""Converts classes, properties, etc. to RDF using the GenTax approach"""
	global g
	print "Step 2: Converting to OWL"
	
	if not element_type or element_type == "metadata":
		print "\tprocessing metadata (len g = %d)" % len(g)
		# ontology metadata
		idref = URIRef("") # local ontology
		triple(g, idref, RDF.type, OWL.Ontology)
		if triple(g, idref, DC.title, Literal(metadata.title), language=lang):
			triple(g, DC.title, RDF.type, OWL.AnnotationProperty)
		triple(g, idref, RDFS.label, Literal(metadata.label), language=lang)
		triple(g, idref, RDFS.comment, Literal(metadata.description), language=lang)
		if triple(g, idref, DC.creator, Literal(metadata.creator), language=lang):
			triple(g, DC.creator, RDF.type, OWL.AnnotationProperty)
		if triple(g, idref, DC.contributor, Literal(metadata.contributor), language=lang):
			triple(g, DC.contributor, RDF.type, OWL.AnnotationProperty)
		if triple(g, idref, DC.rights, Literal(metadata.rights), language=lang):
			triple(g, DC.rights, RDF.type, OWL.AnnotationProperty)
		if triple(g, idref, DC.subject, Literal(metadata.subject), language=lang):
			triple(g, DC.subject, RDF.type, OWL.AnnotationProperty)
		triple(g, idref, DCTERMS.license, rdflib.URIRef(metadata.license))
		triple(g, idref, OWL.versionInfo, Literal(metadata.version), language=lang)
		triple(g, idref, RDFS.seeAlso, rdflib.URIRef(metadata.seeAlso))
		triple(g, idref, OWL.imports, rdflib.URIRef(ontologies["gr"][:-1]))
		triple(g, SELF.hierarchyCode, RDF.type, OWL.AnnotationProperty)
		if include_annotationprops:
			triple(g, SELF.recommendedValue, RDF.type, OWL.AnnotationProperty)
			triple(g, SELF.recommendedProperty, RDF.type, OWL.AnnotationProperty)
		# serialize and reset
		if not config.dump_mode:
			graphFlush("pretty-xml", "O_%s.rdf" % config.ns)
		serializeHTML() # serialize ontology metadata to HTML page

	if not element_type or element_type == "classes":
		print "\tprocessing %d classes / applying gentax approach (len g = %d)" % (len(classes), len(g))
		gentax(classes) # gen/tax algorithm on classes

	if not element_type or element_type == "properties":
		print "\tprocessing %d properties (len g = %d)" % (len(properties), len(g))
		domains = {}
		for p in properties:
			if not p.id: # skip empty ids
				print "\t\tskipped empty id"
				continue
			idf = "P_"+p.id
			idref = URIRef(idf)
			# [<objecttype>, <datatype>], e.g. ["quantitative", "float"]
			object_type = "datatype"
			datatype = "string"
			if p.type:
				object_type = p.type[0]
				datatype = p.type[1]	
			
			if object_type == "quantitative":
				triple(g, idref, RDF.type, OWL.ObjectProperty)
				triple(g, idref, RDFS.subPropertyOf, GR.quantitativeProductOrServiceProperty)
				if datatype == "float":
					triple(g, idref, RDFS.range, GR.QuantitativeValueFloat)
				elif datatype == "integer":
					triple(g, idref, RDFS.range, GR.QuantitativeValueInteger)
				else:
					triple(g, idref, RDFS.range, GR.QuantitativeValue)
			elif object_type == "datatype":
				triple(g, idref, RDF.type, OWL.DatatypeProperty)
				triple(g, idref, RDFS.subPropertyOf, GR.datatypeProductOrServiceProperty)
				if datatype == "string":
					triple(g, idref, RDFS.range, XSD.string)
				elif datatype == "float":
					triple(g, idref, RDFS.range, XSD.float)
				elif datatype == "integer":
					triple(g, idref, RDFS.range, XSD.int)
				elif datatype == "boolean":
					triple(g, idref, RDFS.range, XSD.boolean)
				elif datatype == "date":
					triple(g, idref, RDFS.range, XSD.dateTime)
				else:
					triple(g, idref, RDFS.range, XSD.string)
			else: # supposed to be qualitative
				triple(g, idref, RDF.type, OWL.ObjectProperty)
				triple(g, idref, RDFS.subPropertyOf, GR.qualitativeProductOrServiceProperty)
				triple(g, idref, RDFS.range, GR.QualitativeValue)
			
			label = p.label
			triplifyResource(idref, RDFS.label, label)
			description = label
			if p.description:
				description = p.description
			triplifyResource(idref, RDFS.comment, description)
			triple(g, idref, RDFS.isDefinedBy, URIRef(""))
					
			# attach annotations if required
			if include_annotationprops and idf in recommended_values:
				for iidf in set(recommended_values[idf]):
					triple(g, idref, SELF.recommendedValue, URIRef(iidf))
			
			# serialize and reset
			if not config.dump_mode:
				graphFlush("pretty-xml", "%s.rdf" % idf)		
			
			if p.domain:
				if idf not in domains:
					domains[idf] = []
				cidf_gen = "C_"+p.domain+"-gen"
				domains[idf].append(URIRef(cidf_gen))
			
		print "\t\tprocessing %d domains of properties (len g = %d)" % (len(domains), len(g))
		# append domains to bnode unionof construct... very very slow
		for k, v in domains.items():
			if not config.dump_mode:
				loadGraph("%s.rdf" % k) # load property graph where to attach the domains
			v = set(v)
			if len(v) == 1:
				triple(g, URIRef(k), RDFS.domain, v.pop())
			elif len(v) > 1:
				items_string = ""
				"""
				for value in v:
					items_string += "<owl:Class rdf:about=\"%s\"></owl:Class>" % str(value)	
				data = "<?xml version=\"1.0\" encoding=\"utf-8\"?><rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" xmlns:rdfs=\"http://www.w3.org/2000/01/rdf-schema#\" xmlns:owl=\"%s\"><rdf:Description rdf:about=\"%s\"><rdfs:domain><owl:Class><owl:unionOf rdf:parseType=\"Collection\">%s</owl:unionOf></owl:Class></rdfs:domain></rdf:Description></rdf:RDF>" % (ontologies["owl"], str(URIRef(k)), items_string)
				#g.parse(data=data, format="xml")
				"""
				# CAUTION: takes very long... needs rdflib XML Serializer hack
				collection = BNode()
				bclass = BNode()
				c = Collection(g, collection, v) # append list of values v to collection c
				triple(g, URIRef(k), RDFS.domain, bclass)
				triple(g, bclass, OWL.unionOf, collection)
				triple(g, bclass, RDF.type, OWL.Class) # don't do that, otherwise you will get nasty data
				#"""
			# serialize and reset
			if not config.dump_mode:
				graphFlush("pretty-xml", "%s.rdf" % k)
		
		"""		
		# attach annotations if required
		if include_annotationprops:
			for cidf, v in domains.items():
				v = set(v)
				for cidref in v:
					cidf = str(cidref)[len(base_uri):]
					if not config.dump_mode:
						print "\t\tpost-processing class file %s with property %s" % (cidf, pidf)
						loadGraph("%s.rdf" % cidf) # load persistent graph for update
					triple(g, cidref, SELF.recommendedProperty, URIRef(pidf))
					if not config.dump_mode:
						graphFlush("pretty-xml", "%s.rdf" % cidf) # store updated property graph
		"""

	if not element_type or element_type == "individuals":
		print "\tprocessing %d individuals (len g = %d)" % (len(individuals), len(g))
		for i in individuals:
			if not i.id: # skip empty ids
				print "\t\tskipped empty id"
				continue
			idf = "V_"+i.id
			idref = URIRef(idf)
			if i.type[0] == "datatype":
				print "\t\tskipped value of datatype property"
				continue
			elif i.type[0] == "quantitative":
				if i.type[1] == "integer":
					triple(g, idref, RDF.type, GR.QuantitativeValueInteger)
				elif i.type[1] == "float":
					triple(g, idref, RDF.type, GR.QuantitativeValueFloat)
				else:
					triple(g, idref, RDF.type, GR.QuantitativeValue)
			else:
				triple(g, idref, RDF.type, GR.QualitativeValue)
			if i.uom:
				triple(g, idref, GR.hasUnitOfMeasurement, Literal(i.uom), datatype=XSD.string)
			label = i.label
			triplifyResource(idref, RDFS.label, label)
			description = label
			if i.description:
				description = i.description
			triplifyResource(idref, RDFS.comment, description)
			triple(g, idref, RDFS.isDefinedBy, URIRef(""))
			
			# serialize and reset
			if not config.dump_mode:
				graphFlush("pretty-xml", "%s.rdf" % idf)
			
			"""
			# linkage (through annotation property) between property and object instance
			if include_annotationprops and i.prop_id:
				pidf = "P_"+i.prop_id
				if not config.dump_mode:
					print "\t\tpost-processing property file %s with value %s" % (pidf, idf)
					loadGraph("%s.rdf" % pidf) # load persistent graph for update
				triple(g, URIRef(pidf), SELF.recommendedValue, idref)
				if not config.dump_mode:
					graphFlush("pretty-xml", "%s.rdf" % pidf) # store updated property graph
			"""

def serialize(format="pretty-xml", filename=None):
	"""Serializes the graph"""
	global g
	if config.dump_mode:
		print "Step 3: Serializing graph (len g = %d)" % len(g)

	if not filename:
		print g.serialize(format=format)#, base=ontologies[ns][:-1]) # does not work, because rdflib does not use xml:base
	else:
		filename = "%s/%s" % (out_dir, filename)
		f = open(filename, "w")
		f.write(g.serialize(format=format))#, base=ontologies[ns][:-1]))
		f.close()
		if config.dump_mode:
			print "\tserialized graph as %s to %s" % (format, filename)
