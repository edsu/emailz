#!/usr/bin/env python

"""
Turns mbox files into rdf, using NEPOMUK Message Ontology.
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

template = """
<html>
    <head>
        <title>%(title)s</title>
        <style>
            header {
                text-align: center;
            }

            #chart {
                width: 1000px;
                margin-left: auto;
                margin-right: auto;
            }

            .node text {
                pointer-events: none;
                font: 10px sans-serif;
            }

        </style>
        <script>
        var emailData = %(json_data)s
        </script>
        <script src="http://d3js.org/d3.v2.js"></script>
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>

        <script>
            $(document).ready(init);

            function init() {
                var height = 1000;
                var width = 1000;
                var color = d3.scale.category20c();
                var pallete = [
                  "#3182bd", "#6baed6", "#9ecae1", "#c6dbef",
                  "#e6550d", "#fd8d3c", "#fdae6b", "#fdd0a2",
                  "#31a354", "#74c476", "#a1d99b", "#c7e9c0",
                  "#756bb1", "#9e9ac8", "#bcbddc", "#dadaeb",
                  "#636363", "#969696", "#bdbdbd", "#d9d9d9",
                  "#843c39", "#ad494a", "#d6616b", "#e7969c",
                  "#7b4173", "#a55194", "#ce6dbd", "#de9ed6"
                ];
                var color = d3.scale.ordinal().range(pallete);

                var force = d3.layout.force()
                    .charge(-50)
                    .linkDistance(10)
                    .size([width, height]);

                var svg = d3.select("#chart").append("svg")
                    .attr("width", width)
                    .attr("height", height)
                
                force
                    .nodes(emailData.nodes)
                    .links(emailData.links)
                    .start();

                var link = svg.selectAll("line.link")
                    .data(emailData.links)
                    .enter().append("line")
                    .attr("class", "link")
                    .style("stroke", "#999")
                    .style("stroke-width", .9);

                var node = svg.selectAll(".node")
                    .data(emailData.nodes)
                  .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", function(d) {
                        if (! d.replyTo) return 7;
                        else return 4;
                    })
                    .style("fill", function(d) {console.log(d.from); return color(d.from)})
                    .call(force.drag)
                    .attr("href", function(d) {d.url})
                    .on("mouseover", function() {force.stop();})
                    .on("mouseout", function() {force.start();})
                    .on("click", function(d) {window.open(d.url, "_new");});
                node.append("title")
                    //.text(function(d) {return d.name + " (sent " +  d.sent + " emails)";});
                    .text(function(d) {return d.subject + " (from " +  d.from + ")";});
                
                force.on("tick", function() {
                    link.attr("x1", function(d) {return d.source.x})
                        .attr("y1", function(d) {return d.source.y})
                        .attr("x2", function(d) {return d.target.x})
                        .attr("y2", function(d) {return d.target.y});

                    node.attr("cx", function(d) {return d.x;})
                        .attr("cy", function(d) {return d.y;})
                });

            }
        </script>
    </head>
    <body>
        <header><h1>%(title)s</h1></header>
        <div id="chart"></div>
    </body>
</html>
"""

def render(title, json_data):
    return template % ({"title": title, "json_data": json_data})

if __name__ == "__main__":
    mboxes = sys.argv[1:]
    load_mboxes(mboxes)


