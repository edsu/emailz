def render(title, json_data):
    return template % ({"title": title, "json_data": json_data})

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
        <a href="http://github.com/edsu/emailz"><img style="position: absolute; top: 0; right: 0; border: 0;" src="http://s3.amazonaws.com/github/ribbons/forkme_right_gray_6d6d6d.png" alt="Fork me on GitHub" /></a> 
        <header><h1>%(title)s</h1></header>
        <div id="chart"></div>
    </body>
</html>
"""


