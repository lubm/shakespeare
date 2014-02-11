/* This module calls Google Charts API to draw a treemap of the search results 
 * grouped hierarchically by work and character 
 */ 

google.load('visualization', '1', {packages:['treemap']});

function drawChart(arrayData) {
    array = arrayData['array'];
    if (array.length == 2) {
        /* Only the header and the root, no data */
        $('#treemap').hide();
        return;
    }
    $('#treemap').show();
    data = google.visualization.arrayToDataTable(array);
    var tree = new google.visualization.TreeMap(document.
        getElementById('treemap'));
    tree.draw(data, {
        minColor: '#709EC1',
        maxColor: '#B94949',
        fontColor: 'black',
        showScale: true,
        useWeightedAverageForAggregation: false});
}
