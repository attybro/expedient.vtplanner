
var Dx=-20,
	Dy=-20;
var width = 740,
    height = 500,//550
    fill = d3.scale.category20();

// mouse event vars
var selected_node = null,
    selected_link = null,
    mousedown_link = null,
    mousedown_node = null,
    mouseup_node = null;


// init svg
var outer = d3.select("#target")
  .append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .attr("pointer-events", "all");

var vis = outer
  .append('svg:g')
    .call(d3.behavior.zoom().on("zoom", rescale))
    .on("dblclick.zoom", null)
  .append('svg:g')
    .on("mousemove", mousemove)
    .on("mousedown", mousedown)
    .on("mouseup", mouseup);

vis.append('svg:rect')
    .attr('width', width)
    .attr('height', height)
    .attr('fill', 'white');

// init force layout
var force = d3.layout.force()
    .size([width, height])
    .nodes([{}]) // initialize with a single node
    .linkDistance(50)
    .charge(-200)
    .on("tick", tick);


// line displayed when dragging new nodes
var drag_line = vis.append("line")
    .attr("class", "drag_line")
    .attr("x1", 0)
    .attr("y1", 0)
    .attr("x2", 0)
    .attr("y2", 0);

// get layout properties
var nodes = force.nodes(),
    links = force.links(),
    node = vis.selectAll(".node"),
    link = vis.selectAll(".link");

// add keyboard callback
d3.select(window).on("keydown", keydown);

redraw();

// focus on svg
// vis.node().focus();
function mousedown() {
  if (!mousedown_node && !mousedown_link) {
    // allow panning if nothing is selected
    vis.call(d3.behavior.zoom().on("zoom"), rescale);
    return;
  }
}

function mousemove() {
  if (!mousedown_node) return;

  // update drag line
  drag_line
      .attr("x1", mousedown_node.x)
      .attr("y1", mousedown_node.y)
      .attr("x2", d3.svg.mouse(this)[0])
      .attr("y2", d3.svg.mouse(this)[1]);

}

function mouseup() {
  if (mousedown_node) {
    // hide drag line
    drag_line
      .attr("class", "drag_line_hidden")

    if (!mouseup_node) {
      // add node
      var point = d3.mouse(this),
        node = {x: point[0], y: point[1]},
        n = nodes.push(node);

      // select new node
      selected_node = node;
      selected_link = null;
      
      // add link to mousedown node
      links.push({source: mousedown_node, target: node, bw: '1'});
    }
    redraw();
  }
  // clear mouse event vars
  resetMouseVars();
}

function resetMouseVars() {
  mousedown_node = null;
  mouseup_node = null;
  mousedown_link = null;
}

function tick() {
  link.attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

  node.attr("dx", function(d) { return d.x+Dx; })
      .attr("dy", function(d) { return d.y+Dy; })
      .attr("x", function(d) { return d.x+Dx; })
      .attr("y", function(d) { return d.y+Dy; });
 //node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; }); 
 //node.attr("x", function(d) { return d.x; })
//	.attr("cx", function(d) { return d.x; })
  //    	.attr("cy", function(d) { return d.y; });
  //node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });


}

// rescale g
function rescale() {
  trans=d3.event.translate;
  scale=d3.event.scale;

  vis.attr("transform",
      "translate(" + trans + ")"
      + " scale(" + scale + ")");
}

// redraw force layout
function redraw() {
	
  //console.log("Now redraw");
	//console.log(node[0]);
  link = link.data(links);
	//console.log(link);
  link.enter().insert("line", ".node")
      .attr("class", "link")
      .on("mousedown", 
        function(d) { 
          mousedown_link = d; 
          if (mousedown_link == selected_link)
		selected_link = null;
          else 
		selected_link = mousedown_link;
          selected_node = null; 
          redraw(); 
        })

  link.exit().remove();

  link
    .classed("link_selected", function(d) { return d === selected_link; });

  node = node.data(nodes);

//  node.enter().insert("circle")
//	.text(function(d) {var soo="pasa";return soo })
//      	.attr("class", "node")
//      	.attr("r", 5)
//console.log("node")
//console.log( node);
//console.log("nodes")
//console.log( nodes);

node.enter().append("svg:image")
	//.attr("title",function(d){return "switch "+(nodes.indexOf(selected_node)+1)})
	.attr("title",
	function(d){
		if(d['title']!=null){
			title = d['title'];
			}
		else title = "switch-"+node[0].length;
		return title;		
		//return "switch "+(nodes.indexOf(selected_node)+1)
	})
	.attr("type_", function(d){ if(d['type']!=null){
			type = d['type'];
			}
		else type = "default_type";
		return type;		
		//return "switch "+(nodes.indexOf(selected_node)+1)
	})
	.attr("class", "node")
	.attr("xlink:href",function(d){ if(d['type']!=null){
			type = d['type'];
			if (type=="switch") img = "/static/media/default/img/switch.svg";
			else if(type=="vm")	img = "/static/media/default/img/vm.svg";
			}
		else img = "/static/media/default/img/switch.svg";
		return img;		
	})
	//node[0][i]).attr("xlink:href","/static/media/default/img/vm.svg");
	//.attr("xlink:href", "/static/media/default/img/switch.svg")
	.attr("x", -40)
	.attr("y", -40)
	.attr("width", 40)
	.attr("height", 40)
	.attr("name","").attr("memory","default").attr("diskImage","default").attr("virtualization","default").attr("hdType","default")
      	.on("mousedown", 
        function(d) { 
	   //alert("Tasto giu'");
          // disable zoom
          vis.call(d3.behavior.zoom().on("zoom"), null);

          mousedown_node = d;
	//sono sullo stesso nodo --> non fare nulla          
	  if (mousedown_node == selected_node){
		selected_node = null;
		}
          else{
	     selected_node = mousedown_node; 
		}             
	selected_link = null; 

          // reposition drag line
          drag_line
              .attr("class", "link")
              .attr("x1", mousedown_node.x)
              .attr("y1", mousedown_node.y)
              .attr("x2", mousedown_node.x)
              .attr("y2", mousedown_node.y)
              .attr("bw", "1");

          redraw(); 
        })
      .on("mousedrag",
        function(d) {
       //   	redraw();
        })
      .on("mouseup", 
        function(d) {

	//Quando clicco
          if (mousedown_node) {
            mouseup_node = d; 
            if (mouseup_node == mousedown_node) {
		//alert("click sul stesso nodo");
		resetMouseVars();
		return;
		}
		else
            // add link

            var link = {source: mousedown_node, target: mouseup_node, bw:''};
            links.push(link);

            // select new link
            selected_link = link;
            selected_node = null;

            // enable zoom
            vis.call(d3.behavior.zoom().on("zoom"), rescale);
            redraw();
            //alert("collega i 2 nodi");
          } 
        })
    .transition()
      .duration(1050)
      .ease("elastic")
      .attr("r", 6.5);



  node.exit().transition()
      .attr("r", 0)
    .remove();

  node.classed("node_selected", function(d) {
	return d === selected_node; 
	});


  if (d3.event) {
    // prevent browser's default behavior
    d3.event.preventDefault();
  }
  
//dd3.select(node[0]).attr("xlink:href")="/static/media/default/img/vm.svg"
		//for (i=0; i<node[0].length; i++){
			//if ((node[0][i]).attr("type")=="vm")
			//console.log(node[0][i])
			//d3.select(node[0][i]).attr("xlink:href","/static/media/default/img/vm.svg");
			//}

  force.start();

}

function spliceLinksForNode(node) {
  toSplice = links.filter(
    function(l) { 
      return (l.source === node) || (l.target === node); });
  toSplice.map(
    function(l) {
      links.splice(links.indexOf(l), 1); });
}

function keydown() {
  if (!selected_node && !selected_link) return;
  switch (d3.event.keyCode) {
	//console.log("entrato");
    case 46: { // delete
      if (selected_node) {
        nodes.splice(nodes.indexOf(selected_node), 1);
        spliceLinksForNode(selected_node);
      }
      else if (selected_link) {
        links.splice(links.indexOf(selected_link), 1);
      }
      selected_link = null;
      selected_node = null;
      redraw();
      break;
    }
    case 83: {// s
	  //you change switch-vm and viceversa
      if(d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href")=="/static/media/default/img/switch.svg"){
		//console.log("Changed: from switch to vm");
		d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href", "/static/media/default/img/vm.svg");
		myArray = d3.select(node[0][nodes.indexOf(selected_node)]).attr("title").split('-');
		d3.select(node[0][nodes.indexOf(selected_node)]).attr("title", "vm-"+myArray[1]);
		selected_link = null;
        selected_node = null;
	break;
		}
      else if(d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href")=="/static/media/default/img/vm.svg"){
		//console.log("Changed: from vm to switch")
		d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href", "/static/media/default/img/switch.svg");
		myArray = d3.select(node[0][nodes.indexOf(selected_node)]).attr("title").split('-');
		d3.select(node[0][nodes.indexOf(selected_node)]).attr("title", "switch-"+myArray[1]);
		selected_link = null;
        selected_node = null;
	break;
		}
	//alert("pippo");

     }
    case 77: {// m
		if(selected_link!=null)
			popUpLink(selected_link)
		else if(selected_node!=null){
			if(d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href")=="/static/media/default/img/switch.svg"){
				popUpSwitch(d3.select(node[0][nodes.indexOf(selected_node)]).attr("title"), node)
				}
			else if(d3.select(node[0][nodes.indexOf(selected_node)]).attr("xlink:href")=="/static/media/default/img/vm.svg"){
				popUpVm(selected_node, node)
			}
		}
	//alert("modify the switch");
      selected_link = null;
      selected_node = null;
	break;
     }
    case 73: {// i
	alert("info ");
	  //console.log(d3.select(links))
      selected_link = null;
      selected_node = null;
	break;
     }
  }
}
//sobstitute by the save function
function firstCheck() {
	toXml()
	getResource();
//alert("alert me, please!!");
}

//convert the array to a xml string 
function toXml() {
	
	nodeArray = new Array();
	//header	
	strBack="<?xml version=\"1.1\" encoding=\"UTF-8\"?> <rspec xmlns=\"http://www.geni.net/resources/rspec/3\" xmlns:xs=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:openflow=\"/opt/foam/schemas\" xs:schemaLocation=\"http://www.geni.net/resources/rspec/3  http://www.geni.net/resources/rspec/3/request.xsd  /opt/foam/schemas /opt/foam/schemas/of-resv-3.xsd\" type=\"request\">"	//slice Info
	strBack+= "<openflow:sliver email=\"roberto.riggio@create-net.org\" description=\"My GENI experiment\"> \
	<openflow:controller url=\"tcp:localhost:9933\" type=\"primary\" /> \
	<openflow:vertigo algorithm=\"vtplanner\" ofversion=\"1.0\" >";


	//switch Info
	strBack+="<openflow:vertices>";
	//console.log(node[0]);
	if (node[0].length==0){
		//console.log("No Nodes");
		}
	else{
		//console.log("Parse Nodes: "+node[0].length);	
		
		for (i=0; i<node[0].length; i++){
			tmp =new Object();	
			tmpEl = d3.select(node[0][i]);
			if(tmpEl!=null){
				//console.log(tmpEl);
				tmp.id = tmpEl.attr("title");
				tmp.x  = tmpEl.attr("x");
				tmp.y  = tmpEl.attr("y");
				splitName=tmp.id.split('-');
				if(splitName[0]=="switch")
				strBack+="<openflow:vertex type=\"switch\" name=\""+tmp.id+"\" dpid=\""+tmp.id+"\" tablesize=\"medium\" switchtype=\"hw\"/>";
				nodeArray.push(tmp);
			}	
		};
		
		
		//VM info 
		//strBack+="<openflow:vms>";
		for (i=0; i<node[0].length; i++){
			tmpEl = d3.select(node[0][i]);
			if(tmpEl!=null){
				//console.log(tmpEl);
				splitName=tmpEl.attr("title").split('-');
				if(splitName[0]=="vm")
					strBack+="<openflow:vertex type=\"vm\" name=\""+tmp.id+"\" dpid=\""+tmp.id+"\" memory=\"256\" cpus_number=\"2\" cpu_frequency=\"2500\" />";
					//strBack+="<openflow:vm id=\""+tmp.id+"\" tablesize=\"medium\" switchtype=\"hw\"/>";
			}	
		};
		strBack+="</openflow:vertices>";
		//strBack+="</openflow:vms>";
		//console.log(nodeArray);
	}

	/////////////////////////////
	//////////link Info//////////
	/////////////////////////////
	strBack+="<openflow:edges>";
	if (link[0].length==0){
		//console.log("No Links");
	}
	else{
			//console.log("Parse Links");
			//console.log(link[0].length);
			for (j=0; j<link[0].length; j++){
				srcId=null;
				dstId=null;
				band='1G';
			if(link[0][j]!=null){
			tmpLink = d3.select(link[0][j]);
			//console.log(tmpLink.attr("x1"));
			if (tmpLink.attr("bw")!=null)band=tmpLink.attr("bw");
			if (nodeArray.length!=0 ){
				nodeArray.forEach(function(tmpNod){

							if ((tmpNod.x-Dx)==tmpLink.attr("x1") && (tmpNod.y-Dy)==tmpLink.attr("y1"))
								srcId=tmpNod.id
								
							if ((tmpNod.x-Dx)==tmpLink.attr("x2") && (tmpNod.y-Dy)==tmpLink.attr("y2"))
								dstId=tmpNod.id
					});
			}

			}
			//console.log("from: "+srcId+" to: "+dstId);
			if (srcId!=null && dstId!=null)
			strBack+="<openflow:edge srcDPID=\""+srcId+"\"  dstDPID=\""+dstId+"\" bw=\""+band+"\"/>";
			}
			
		}
	strBack+="</openflow:edges>";

	   //   <openflow:edge src="sw1" dst="sw2" bw="10M"/>
	   //   <openflow:edge src="sw1" dst="sw3" bw="100K"/>
	   //   <openflow:edge src="sw3" dst="sw4" bw="1G"/>
	   //   <openflow:edge src="sw3" dst="vm1" bw="1G"/>
strBack+="<openflow:match>\
             <openflow:packet>\
                <openflow:nw_src value=\"10.1.1.0\/24\" />\
                <openflow:dl_type value=\"0x810, 0x811\" />\
             </openflow:packet>\
          </openflow:match>";
	   

	   
	   
	//slice Bottom
	strBack+="</openflow:vertigo></openflow:sliver> </rspec>";
	//console.log("call the checkAvailability:")
	//console.log(strBack);
	checkAvailability(strBack);
	//return strBack;
}



function redrawFromJson(jsonFile){

if (jsonFile!=null){

	var nodi = [];
	var connection=[];
	obj = JSON.parse(jsonFile);
	//console.log(obj);
	//console.log(obj[]);
	vert=false;
	for (var i=0;i<obj.length;i++){
		//console.log(obj[i]);
		tmp=obj[i];
		if(tmp.vertices!=null){
			var passVert=tmp.vertices;
			//console.log("VERTICES")
			//console.log(passVert)
			nodi=giveNodesJson(passVert)
		}
		if(tmp.edges!=null){
			//console.log("EDGES")
			var passEdge=tmp.edges;
			connection=giveEdgesJson(passEdge,nodi)
			//console.log(connection)
		}
		if(tmp.matches!=null){
			//console.log("MATCHES")
			//giveMatchesJson(tmp.matches)
		}
	}
	
	if (nodi.length>0){
		vis.selectAll(".node").remove();//remove all the previous node	
		vis.selectAll(".links").remove();//remove all the previous node	
	}
	//vert=obj['vertices'];
	//console.log(obj["vertices"])
	//if (vert.length>0){
	//		for (var i=0;i<vert.length;i++){
			//console.log(vert[i]);
	//		}
	//	}
	//else nodi=[{}];
	
	//link2 =new Object();
	//link2={"source": nodi[0], "target":nodi[1]};
	force = d3.layout.force()
    .size([width, height])
	.nodes(nodi)
	.links(connection)
    .linkDistance(50)
    .charge(-200)
    .on("tick", tick);



// get layout properties
	nodes = force.nodes(),
    links = force.links(),
    node = vis.selectAll(".node"),
    link = vis.selectAll(".link");

	// add keyboard callback
	d3.select(window).on("keydown", keydown);
	redraw();

	}
}

	

function giveNodesJson(jsonFile){
	
	//console.log(jsonFile);
	//obj = JSON.parse(jsonFile);
	//console.log(obj);
	var nodeBack = [];
	for (var i=0;i<jsonFile.length;i++){
	//console.log(jsonFile[i])
	if (jsonFile[i].type=="switch"){
	//console.log('uno sw')
		tmpNode	={
             nodeValue: jsonFile[i].dpid, nodeName: jsonFile[i].switchtype,
             image: "d3Test/switch.svg", color: "", title:jsonFile[i].dpid,
             group: "", location: "", type: jsonFile[i].type,
             description: "aallala",
	   };
	   nodeBack.push(tmpNode)
	   }
	   else if(jsonFile[i].type=="vm"){
	   //console.log('una ')
	   		tmpNode	={
             nodeValue: jsonFile[i].dpid, nodeName: jsonFile[i].switchtype,
             image: "d3Test/vm.svg", color: "", title:jsonFile[i].dpid,
             group: "", location: "", type: jsonFile[i].type,
             description: "aallala",
	   };
	   nodeBack.push(tmpNode)
	   }
	   
		//console.log(jsonFile[i].switchtype);
	}
	 console.log(nodeBack);

	 return nodeBack;
	}
	
	
function	giveEdgesJson(passEdge,nodi){
	//console.log("edge estraction ")
	//console.log(passEdge)
	//console.log(nodi)
	var linkBack = [];
	for (var i=0;i<passEdge.length;i++){
		bw=passEdge[i].bw;
		console.log(passEdge[i].bw)
		console.log(passEdge[i].srcDPID+'-----'+passEdge[i].dstDPID)
		for (var j=0; j<nodi.length; j++ ){
			if (passEdge[i].srcDPID==nodi[j].nodeValue){
				srcN=nodi[j]
				
			}
			if (passEdge[i].dstDPID==nodi[j].nodeValue){
				dstN=nodi[j]
			}
		}
		tmpLink	={
             source: srcN, target: dstN, bw:bw,
	   };
		linkBack.push(tmpLink)
	}
	return linkBack;
}



