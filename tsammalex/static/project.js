TSAMMALEX = {};

TSAMMALEX.style = function(feature) {
    return {
            'color': '#000',
            'weight': 1,
            'opacity': 0.3,
            'fillOpacity': 0.3,
            'fillColor': '#' + feature.properties.color
    }
};

TSAMMALEX.highlight = undefined;

TSAMMALEX.highlightEcoregion = function(layer) {
    var style = TSAMMALEX.style(layer.feature);
    if (TSAMMALEX.highlight) {
        TSAMMALEX.highlight.setStyle(TSAMMALEX.style(TSAMMALEX.highlight.feature));
    }
    TSAMMALEX.highlight = layer;
    style.weight = 3;
    style.color = '#f00';
    style.opacity = 0.8;
    layer.setStyle(style);
    CLLD.mapShowInfoWindow('map', layer, layer.feature.properties.latlng);
    return false;
};

CLLD.LayerOptions.ecoregions = {
    style: TSAMMALEX.style,
    onEachFeature: function(feature, layer) {
        layer.bindLabel(feature.properties.label);
        CLLD.Maps.map.marker_map[feature.properties.id] = layer;

        // Create a self-invoking function that passes in the layer
        // and the properties associated with this particular record.
        (function(layer, properties) {
            layer.on('click', function(e) {
                CLLD.mapShowInfoWindow('map', layer, e.latlng);
            });
            // Close the "anonymous" wrapper function, and call it while passing
            // in the variables necessary to make the events work the way we want.
        })(layer, feature.properties);
    }
};
