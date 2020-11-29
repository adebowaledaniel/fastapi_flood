var map = L.map('map').setView([47.8090549,13.0351476], 8);
L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png', {
    maxZoom: 18,
    attribution: 'Map data &copy; OpenStreetMap contributors'
}).addTo(map);
L.Control.geocoder().addTo(map);

map.pm.addControls({
  position: 'topleft',
  drawCircle: false,
  drawMarker: false,
  drawCircleMarker: false,
  drawPolyline: false,
  drawPolygon: false,
  editMode: false,
  cutPolygon: false
});

var sidebar = L.control.sidebar('sidebar').addTo(map);
sidebar.open('home');


function sendbbox() {
  var layers = L.PM.Utils.findLayers(map);
  var group = L.featureGroup();
  layers.forEach((layer)=>{
        group.addLayer(layer);
  });
  shapes = bbox(group.toGeoJSON());
  if (shapes[0] == "Infinity") {
    var area_name = document.getElementById("select").value
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
    document.getElementById("xmin").value = shapes[0].toFixed(3);
    document.getElementById("ymin").value = shapes[1].toFixed(3);
    document.getElementById("xmax").value = shapes[2].toFixed(3);
    document.getElementById("ymax").value = shapes[3].toFixed(3);
  } 
  var xmean = (parseFloat(document.getElementById("xmin").value) + parseFloat(document.getElementById("xmax").value))/2
  var ymean = (parseFloat(document.getElementById("ymin").value) + parseFloat(document.getElementById("ymax").value))/2
  map.setView([ymean, xmean], 15);
}

