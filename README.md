emailz
======

emailz is a utility for turning discussion list mboxes into rdf using the 
NEPOMUK Message Ontology. It includes a simple tool that reads the rdf 
to visualize threads in an email discussion list using D3. I've been using
it as a discovery tool for some historical research I'm doing.

See the examples directory for sample rdf and html files.

Disclaimer
----------

emailz was really only tested on the mboxes for w3c discussion lists, so it
may not work for you. Pull requests welcome!

Usage
-----

1. pip install rdflib
1. ./mbox2rdf.py \*.mbx > emails.rdf
1. ./threads.py emails.rdf > threads.html
1. open threads.html

Lincense
--------

* CC0
