#!/usr/bin/env python

"""
Print out an HTML visualization of the people who have corresponded.
"""

import sys
import json
import rdflib

from mbox2rdf import nmo, scrub, render

g = rdflib.Graph()
g.parse(sys.argv[1])

# create graph of people who have corresponded with each other

people = set()
correspondence = []
senders = {} 

for email, from_email in g.subject_objects(nmo["from"]):
    from_email = scrub(from_email)
    people.add(from_email)
    senders[from_email] = senders.get(from_email, 0) + 1

    for to_email in g.objects(email, nmo.to):
        to_email = scrub(to_email)
        people.add(to_email)
        correspondence.append((from_email, to_email))

    for cc_email in g.objects(email, nmo.to):
        cc_email = scrub(cc_email)
        people.add(cc_email)
        correspondence.append((from_email, cc_email))

people = list(people)
people.sort()
people = [{"name": v, "sent": senders.get(v, 0)} for v in people]
people = filter(lambda p: p["sent"] != 0, people)
people_ids = [p["name"] for p in people]

links = []
for a, b in correspondence:
    if a in people_ids and b in people_ids:
        links.append({
            "source": people_ids.index(a),
            "target": people_ids.index(b),
        })

d3 = {"nodes": people, "links": links} 
json_data = json.dumps(d3, indent=2)

print render("People", json_data)
