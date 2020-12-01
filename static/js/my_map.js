var map = L.map('map').setView([48.303,16.865], 15);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
    attribution: 'Map data &copy; OpenStreetMap contributors'
}).addTo(map);
//L.Control.geocoder().addTo(map);

let drawItems = new L.FeatureGroup();
map.addLayer(drawItems);

var drawControl = new L.Control.Draw({
    draw: {
        toolbar: {
            buttons: {
                polygon: 'Draw an awesome polygon'
                    }
                 }
           },
    edit: {
        featureGroup: drawItems,
        poly: {
            allowIntersection: false
        }
    }
})
map.addControl(drawControl);

map.on("draw:created", function(e) {
  //cleanMap();
  let type = e.layerType;
  var layer = e.layer;

  var shape = layer.toGeoJSON()
  console.log(shape);
  var shape_for_db = JSON.stringify(shape);
  console.log(shape_for_db);

  drawItems.addLayer(layer);

  var shapes = getShapes(drawItems);
});

var getShapes = function(drawItems){
    var shapes = [];
    drawItems.eachLayer(function(layer){
        if (layer instanceof L.Polyline){
            shapes.push(layer.getLatLngs())
        }
        if (layer instanceof L.Circle) {
            shapes.push([layer.getLatLng()])
        }
        if (layer instanceof L.Marker) {
            shapes.push([layer.getLatLng()]);
        }
    });
    return shapes;
};

var cleanMap = function(){
    for(i in m._layers) {
        if(m._layers[i]._path != undefined) {
            try {
                m.removeLayer(m._layers[i]);
            }
            catch(e) {
                console.log("problem with " + e + m._layers[i]);
            }
        }
    }
};

var sidebar = L.control.sidebar('sidebar').addTo(map);
sidebar.open('home');

function sendbbox() {
    var area_name = document.getElementById("select").value
    if (area_name != "none") {  
      switch (area_name) {
        case "baumgarten":
          document.getElementById("xmin").value = 16.865;
          document.getElementById("ymin").value = 48.282;
          document.getElementById("xmax").value = 16.904;
          document.getElementById("ymax").value = 48.303;
          break;
        case "jedenspeigen":
          document.getElementById("xmin").value = 16.882;
          document.getElementById("ymin").value = 48.492;
          document.getElementById("xmax").value = 16.920;
          document.getElementById("ymax").value = 48.512;
          break;
        case "droesing":
          document.getElementById("xmin").value = 16.906;
          document.getElementById("ymin").value = 48.516;
          document.getElementById("xmax").value = 16.946;
          document.getElementById("ymax").value = 48.535;
          break;
        case "hohenau":
          document.getElementById("xmin").value = 16.909;
          document.getElementById("ymin").value = 48.600;
          document.getElementById("xmax").value = 16.946;
          document.getElementById("ymax").value = 48.620;
          break;
        case "rabensburg":
          document.getElementById("xmin").value = 16.899;
          document.getElementById("ymin").value = 48.628;
          document.getElementById("xmax").value = 16.937;
          document.getElementById("ymax").value = 48.648;
          break;
        case "duernkrut":
          document.getElementById("xmin").value = 16.853;
          document.getElementById("ymin").value = 48.459;
          document.getElementById("xmax").value = 16.892;
          document.getElementById("ymax").value = 48.479;
        case "stillfried":
          document.getElementById("xmin").value = 16.833;
          document.getElementById("ymin").value = 48.410;
          document.getElementById("xmax").value = 16.867;
          document.getElementById("ymax").value = 48.429;
          break;
        case "marchegg":
          document.getElementById("xmin").value = 16.920;
          document.getElementById("ymin").value = 48.252;
          document.getElementById("xmax").value = 16.959;
          document.getElementById("ymax").value = 48.272;
          break;
        case "angern":
          document.getElementById("xmin").value = 16.824;
          document.getElementById("ymin").value = 48.370;
          document.getElementById("xmax").value = 16.850;
          document.getElementById("ymax").value = 48.387;
          break;
      }
    } else {
        // Updgrade bbox
        var data = drawItems.getBounds().toBBoxString();
        var shapes = data.split(",");    
        document.getElementById("xmin").value = parseFloat(shapes[0]).toFixed(3);
        document.getElementById("ymin").value = parseFloat(shapes[1]).toFixed(3);
        document.getElementById("xmax").value = parseFloat(shapes[2]).toFixed(3);
        document.getElementById("ymax").value = parseFloat(shapes[3]).toFixed(3);
    }
    var xmean = (parseFloat(document.getElementById("xmin").value) + parseFloat(document.getElementById("xmax").value))/2
    var ymean = (parseFloat(document.getElementById("ymin").value) + parseFloat(document.getElementById("ymax").value))/2
    map.setView([ymean, xmean], 15);
}

