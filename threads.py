#!/usr/bin/env python

"""
Print out an HTML visualization of the email threads in a given set of messages.

  % ./threads.py emails.rdf > threads.html

"""

import sys
import json
import rdflib

from mbox2rdf import nmo, scrub
from template import render

rdf_file = sys.argv[1]

g = rdflib.Graph()
g.parse(rdf_file)

emails = set()
replies = []
for reply, orig in g.subject_objects(nmo.inReplyTo):
    emails.add(reply)
    emails.add(orig)
    replies.append((reply, orig))

emails = list(emails)
emails.sort()
email_nodes = []
for email in emails:
    f = g.value(email, nmo["from"], None)
    s = g.value(email, nmo.messageSubject, None)
    r = g.value(email, nmo.inReplyTo, None)

        
    if f and s:
        f = f.replace("mailto:", "")
        e = {
            "subject": s, 
            "from": f,
            "url": email,
            "replyTo": r
        }
        email_nodes.append(e);

emails = [e["url"] for e in email_nodes]
links = []
for a, b in replies:
    if a in emails and b in emails:
        links.append({
            "source": emails.index(a),
            "target": emails.index(b)
        })

d3 = {"nodes": email_nodes, "links": links}
json_data = json.dumps(d3, indent=2)

print render("Threads in %s" % rdf_file, json_data)
