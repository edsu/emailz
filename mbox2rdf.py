#!/usr/bin/env python

"""
Turns mbox files into rdf, using NEPOMUK Message Ontology. You may want
to extract more from the mbox. Please send a pull request if you do!
"""

import os
import sys
import rdflib
import rfc822
import mailbox 
import datetime

nmo = rdflib.Namespace("http://www.semanticdesktop.org/ontologies/nmo/#")
rdf = rdflib.RDF
uri = rdflib.URIRef

def load_mboxes(mboxes):
    g = rdflib.Graph(identifier="emails")
    g.bind("nmo", str(nmo))
    for msg in get_messages(mboxes):
        u = uri(msg["url"])
        g.add((u, rdf.type, nmo.Email))
        g.add((u, nmo["from"], uri("mailto:" + msg["from"][1])))
        g.add((u, nmo.sentDate, rdflib.Literal(msg["date"])))
        g.add((u, nmo.messageSubject, rdflib.Literal(msg["subject"])))
        g.add((u, nmo.messageId, rdflib.Literal(msg["message_id"])))
        for name, email in msg["to"]:
            g.add((u, nmo.to, uri("mailto:" + email)))
        for name, email in msg["cc"]:
            g.add((u, nmo.cc, uri("mailto:" + email)))
        if msg["in_reply_to"]:
            reply_to = msg["in_reply_to"].strip("<>")
            reply_to = "http://www.w3.org/mid/" + reply_to
            reply_to = rdflib.URIRef(reply_to)
            g.add((u, nmo.inReplyTo, reply_to))

    g.serialize(sys.stdout)
    g.close()

def get_messages(mboxes):
    for mbox_file in mboxes:
        for msg in mailbox.mbox(mbox_file):
            yield get_message(msg)

def get_message(msg):
    fr = rfc822.parseaddr(msg['from'])
    to = rfc822.AddressList(msg['to']).addresslist
    cc = rfc822.AddressList(msg['cc']).addresslist
    subject = msg['subject']
    date = rfc822.parsedate(msg['date'])
    date = datetime.datetime(*date[:6])
    url = msg['Archived-At']
    if not url: 
        url = msg['X-Archived-At']
    url = url.strip("<>")
    message_id = msg['Message-ID']
    in_reply_to = msg.get('In-Reply-To', None)

    return {
        "from": fr,
        "subject": subject,
        "to": to,
        "cc": cc,
        "url": url,
        "date": date,
        "message_id": message_id,
        "in_reply_to": in_reply_to,
        "raw": msg.as_string()
    }

    return None

def scrub(email):
    return email.replace("mailto:", "").lower()

if __name__ == "__main__":
    mboxes = sys.argv[1:]
    load_mboxes(mboxes)


