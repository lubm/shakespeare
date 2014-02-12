/* This module calls Google Charts API to draw a treemap of the search results 
 * grouped hierarchically by work and character.
 *
 * The file results.js should be imported first for this to work properly.
 * 
 * The aggregation function was changed using the implementation available in:
 * http://jsfiddle.net/asgallant/NpsUh/7/
 */ 

google.load('visualization', '1', {packages:['treemap', 'controls']});

function drawChart(arrayData) {
    array = arrayData['array'];
    if (!array || array.length == 2) {
        // Only the header and the root, no data
        return;
    }
    $('#treemap').show();
    data = google.visualization.arrayToDataTable(array);
    function setNodeValues(dt, row) {
        var childRows = dt.getFilteredRows([{
            column: 1,
            value: dt.getValue(row, 0)}]);
        if (childRows.length > 0) {
            // this is a parent, recurse down, and set value when w
            var vals = [];
            var tmp;
            for (var i = 0; i < childRows.length; i++) {
                tmp = setNodeValues(dt, childRows[i]);
                vals.push(tmp.val);
            }
            dt.setValue(row, 2, google.visualization.data.sum(vals));
            return {
                val: google.visualization.data.sum(vals)
            };
        }
        else {
            // we're at the bottom, just return the data
            return {
                val: dt.getValue(row, 2)
            }
        }
    }
    
    setNodeValues(data, 0);
    
    // identify all rows necessary for the tree at a given parent node
    function getRowsForNode(dt, row) {
        return [row].concat(dt.getFilteredRows([{
            column: 1,
            value: dt.getValue(row, 0)
        }]));
    }

    var view = new google.visualization.DataView(data);
    view.setRows(getRowsForNode(data, 0));
            
    displayTooltip = function (row, size, value) {
        name = view.getValue(row, 0);
        if (name.indexOf('+') != -1) {
            /* Characters */
            name = name.split('+')[1]; 
        }
        return '<p><b>' + name + '</b></p>' + 
            '<p>' + size + ' results</p>';

    };

    var treemap = new google.visualization.ChartWrapper({
        chartType: 'TreeMap',
        containerId: 'treemap',
        dataTable: view,
        options: {
            minColor: '#709EC1',
            maxColor: '#B94949',
            fontColor: 'black',
            fontSize: '16',
            fontFamily: 'Helvetica Neue',
            showScale: true,
            useWeightedAverageForAggregation: false,
            generateTooltip: displayTooltip
        }
    });

    google.visualization.events.addListener(treemap, 'select', function () {
        var viewRow = treemap.getChart().getSelection()[0].row;
        var row = view.getTableRowIndex(viewRow);
        // if viewRow is 0, go back, unless the DataTable row is also 0
        if (viewRow == 0 && row != 0) {
            // go up the tree instead of down
            row = data.getFilteredRows([{
                column: 0,
                value: data.getValue(row, 1)
            }])[0];
        }
        var rows = getRowsForNode(data, row);
        // only redraw if this isn't a bottom leaf, ie more than 1 row returned
        if (rows.length > 1) {
            view.setColumns([0, {
                type: 'string',
                label: data.getColumnLabel(1),
                calc: function (dt, r) {
                    return (r == row) ? null : dt.getValue(r, 1);
                }
            }, 2]);
            view.setRows(getRowsForNode(data, row));
            treemap.draw();
        }
    });
    
    treemap.draw();

}