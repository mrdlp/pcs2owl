#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
pcs2owl.py

Generates RDF/XML.

Created by Alex Stolz on 2011-03-23.
Copyright (c) 2011 E-Business and Web Science Research Group. All rights reserved.
"""
import sys
import shutil

import config
exec "from import_pcs import %s as pcsmod" % config.ns

def main(elements_loaded=False):
	"""Main function triggers conversion, acts as config controller"""
	if not config.base_uri[-1] in ["#", "/"]: # trailing hash or slash are neccessary at least... e.g. http://www.example.com/ or http://www.example.com/ns#
		sys.exit("ERROR: base_uri does whether contain trailing hash (#) nor slash (/). Please supply any of them!")
	if not config.dump_mode and config.base_uri[-1] == "#": # hash and single file mode do not make sense... filename: C_AB000.rdf and pcs#C_AB000 is wrong!
		sys.exit("ERROR: Single file mode (base_uri/C_XXX.rdf) and hash uris (base_uri#C_XXX) are not allowed in combination!")
	
	if not config.dump_mode:
		print "## WRITE SINGLE FILES ##"
		config.sem_sitemap.write("""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:sc="http://sw.deri.org/2007/07/sitemapextension/scschema.xsd">
""")
	
	if not elements_loaded:
		pcsmod.importData()
	# args: element_type=None
	pcsmod.convert2OWL()
	#pcsmod.convert2OWL("metadata")
	#pcsmod.convert2OWL("classes")
	#pcsmod.convert2OWL("properties")
	#pcsmod.convert2OWL("individuals")
	
	# args: format="pretty-xml", filename=None
	if config.dump_mode: # if not dump_mode, serialization is done inside code
		pcsmod.serialize(format="pretty-xml", filename="%s.rdf" % config.ns)
		pcsmod.serialize(format="n3", filename="%s.n3" % config.ns)
		
	# create htaccess file, if not dump_mode
	if not config.dump_mode:
		print "Step 3: Writing supplementary files"
		# close semantic sitemap
		config.sem_sitemap.write("""</urlset>""")
		print "\twrote semantic sitemap file to %s/sitemap.xml" % config.out_dir
		
		htaccess = "%s/htaccess.txt" % config.out_dir
		f = open(htaccess, "w")
		f.write("""# rename this file to .htaccess when deployed

# Turn off MultiViews
Options -MultiViews

# Rewrite engine setup
RewriteEngine On

# Rewrite rule to serve HTML content from the vocabulary URI if requested
RewriteCond %{HTTP_ACCEPT} text/html [OR]
RewriteCond %{HTTP_ACCEPT} application/xhtml\+xml [OR]
RewriteCond %{HTTP_USER_AGENT} ^Mozilla/.*
RewriteRule ^(.*)$ $1.html

# Rewrite rule to serve RDF/XML content from the vocabulary URI if requested
RewriteCond %{HTTP_ACCEPT} application/rdf+xml
RewriteRule ^(.*)$ $1.rdf [R=303]

# Rewrite rule to serve the RDF/XML content from the vocabulary URI by default 
RewriteRule ^(.*)$ $1.rdf [R=303]
""")
		print "\twrote htaccess-file to %s. Please rename it to .htaccess when deployed on an Apache Web Server." % htaccess
		f.close()
		
		shutil.copy("templates/style.css", config.out_dir)
		shutil.copy("templates/print.css", config.out_dir)
		shutil.copy("templates/bmbf.png", config.out_dir)
		shutil.copy("templates/logo_researchgroup.png", config.out_dir)
		
		print "\tcopied stylesheets and images to %s" % config.out_dir
		
		# maybe also create a dumpfile
		if config.create_dump:
			print "## CREATE DUMPFILE ##"
			# preparing tasks
			config.dump_mode = True
			main(True)
			
		config.sem_sitemap.close()

if __name__ == "__main__":
	main()

# TODO: seeAlso for classes, ontology description?

# TO REMEMBER: save all input files as utf-8 with unix LF!!!
