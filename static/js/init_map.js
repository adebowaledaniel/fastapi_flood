/*
the script mus be loaded after the map div is defined,
otherwise this will not work. Therefore the script is below
the div.
The source code below is the example from the leaflet start page.
*/
var map = L.map('mapid').setView([-11.97586, -77.08767], 18);
L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
L.marker([-11.97586, -77.08767]).addTo(map)
 .bindPopup('Pato & Roy ... forever <3 (nidito de amor)')
 .openPopup();
 
// add leaflet-geoman controls with some options to the map
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
