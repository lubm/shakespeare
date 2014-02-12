/* This module calls Google Charts API to draw a treemap of the search results 
 * grouped hierarchically by work and character.
 *
 * The file results.js should be imported first for this to work properly.
 */ 

google.load('visualization', '1', {packages:['treemap']});

function drawChart(arrayData) {
    array = arrayData['array'];
    if (!array || array.length == 2) {
        /* Only the header and the root, no data */
        return;
    }

    $('#treemap').show();
    data = google.visualization.arrayToDataTable(array);
    
    displayTooltip = function (row, size, value) {
        name = data.getValue(row, 0);
        if (name.indexOf('+') != -1) {
            /* Characters */
            name = name.split('+')[1]; 
        }
        return '<p><b>' + name + '</b></p>' + 
            '<p>' + size + ' results.</p>';

    };

    var tree = new google.visualization.TreeMap(document.
        getElementById('treemap'));
    tree.draw(data, {
        minColor: '#709EC1',
        maxColor: '#B94949',
        fontColor: 'black',
        fontSize: '16',
        fontFamily: 'Helvetica Neue',
        showScale: true,
        useWeightedAverageForAggregation: false,
        generateTooltip: displayTooltip
    });

}
