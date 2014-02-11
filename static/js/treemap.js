/* This module calls Google Charts API to draw a treemap of the search results 
 * grouped hierarchically by work and character.
 *
 * The file results.js should be imported first for this to work properly.
 */ 

google.load('visualization', '1', {packages:['treemap']});

function drawChart(arrayData) {
    array = arrayData['array'];
    if (array.length == 2) {
        /* Only the header and the root, no data */
//       message = document.createElement('p');
//        $(message).append(document.createTextNode('No results found for '));
//        word = document.createElement('span');
//        $(word).text(getSearchedWord());
//        $(word).attr('style', 'font-style: italic;');
//        $(message).append(word);
//        $('#treemap').before(message);
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
