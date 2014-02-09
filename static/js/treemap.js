/* This module calls Google Charts API to draw a treemap of the search results 
 * grouped hierarchically by work and character 
 */ 

google.load('visualization', '1', {packages:['treemap']});

function drawChart(arrayData) {
    data = google.visualization.arrayToDataTable(arrayData["array"]);
    var tree = new google.visualization.TreeMap(document.
        getElementById('treemap'));
    tree.draw(data, {
        minColor: '#CCC',
        midColor: '#709EC1',
        maxColor: '#B04949',
        fontColor: 'black',
        showScale: true});
}

$(document).ready(function() {
    var request = {
        searched_word: $('#search-value').val()
    };
    /* Call for receiving treemap data */
    $.get('/treemap', request, drawChart);
});
