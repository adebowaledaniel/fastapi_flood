var map = L.map('map').setView([47.8090549,13.0351476], 12);
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

function sendbbox() {
  var layers = L.PM.Utils.findLayers(map);
  var group = L.featureGroup();
  layers.forEach((layer)=>{
        group.addLayer(layer);
  });
  shapes = bbox(group.toGeoJSON());

  // Updgrade bbox
  document.getElementById("xmin").value = shapes[0].toFixed(3);
  document.getElementById("ymin").value = shapes[1].toFixed(3);
  document.getElementById("xmax").value = shapes[2].toFixed(3);
  document.getElementById("ymax").value = shapes[3].toFixed(3);

  // Change View of leaflet map
  //var xmean = (shapes[0] + shapes[2])/2;
  //var ymean = (shapes[1] + shapes[3])/2;
  //map.setView(new L.LatLng(ymean, xmean), 12);          
}