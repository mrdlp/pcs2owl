#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
google.py

Google Product Type Taxonomy import module
- http://www.google.com/basepages/producttype/taxonomy.en-US.txt

Created by Alex Stolz on 2013-02-11.
Copyright (c) 2013 E-Business and Web Science Research Group. All rights reserved.
"""
import codecs

from util import * # imports also config, classes, rdflib, ...
import util

def importData():
    """Loading facility"""
    print "Step 1: Loading PCS from %s" % __name__
    
    # ONTOLOGY: def __init__(self, title="", label="", description="", creator="", contributor="", rights="", subject="", license="", version="", seeAlso=""):
    util.metadata = Ontology("Google", label="Google Product Type Taxonomy", creator="Alex Stolz", contributor="Bene Rodriguez-Castro", version="1.0")
    
    f = codecs.open("pcs/google/taxonomy.en-US.txt", encoding="utf-8", mode="r")
    first_line = True
    last_tokens = []
    for line in list(f):
        line = line.strip()
        tokens = line.split(">")
        tokens = [token.replace("\n", "").strip() for token in tokens]
        tokens_id = [token.replace("&", "and").replace(" ", "_") for token in tokens]
        if len(tokens)>1:
            cappend(Class(tokens_id[-2], tokens_id[-1], tokens[-1], line))
        else:
            cappend(Class("", tokens_id[-1], tokens[-1], line))
            
        
#       # CLASS: def __init__(self, parent_id, class_id, label="", description=""):
#       if len(tokens)>0 and len(last_tokens)>0 and tokens[0] != last_tokens[0]:
# #         print "\t- new segment"
#           cappend(Class("", tokens[0], tokens[1])) # segment
#       if len(tokens)>2 and len(last_tokens)>2 and tokens[2] != last_tokens[2]:
# #         print "\t- new family"
#           cappend(Class(tokens[0], tokens[2], tokens[3])) # family
#       if len(tokens)>4 and len(last_tokens)>4 and tokens[4] != last_tokens[4]:
# #         print "\t- new class"
#           cappend(Class(tokens[2], tokens[4], tokens[5])) # class
#       if len(tokens)>6 and len(last_tokens)>6 and tokens[6] != last_tokens[6]:
# #         print "\t- new brick"
#           cappend(Class(tokens[4], tokens[6], tokens[7])) # brick
#       # PROPERTY: def __init__(self, class_id, prop_id, label="", description=""):
#       if len(tokens)>9:
#           pappend(Property(tokens[6], tokens[8], tokens[9]))
#       # INDIVIDUAL: def __init__(self, prop_id, inst_id, label="", description=""):
#       if len(tokens)>11:
#           iappend(Individual(tokens[8], tokens[10], tokens[11]))
#       last_tokens = tokens
    
def convert2OWL(element_type=None):
    """Dummy function, see util.py"""
    util.convert2OWL(element_type)
    
def serialize(format="pretty-xml", filename=None):
    """Dummy function, see util.py"""
    util.serialize(format, filename)

    
