google.load('visualization', '1', {packages:['treemap']});

function drawChart(arrayData) {
    data = google.visualization.arrayToDataTable(arrayData["array"]);
    var tree = new google.visualization.TreeMap(document.
        getElementById('treemap'));
    tree.draw(data, {
        minColor: '#313BC0',
        midColor: '#fff',
        maxColor: '#C12222',
        fontColor: 'black',
        showScale: true});
}

$(document).ready(function() {
    var request = {
        searched_word: $('#search-value').val()
    };
    console.log(request.searched_word)
    $.get('/treemap', request, drawChart);
});
