$(window).load(function() {
    $('#visualization-tab-content').css('visibility', 'hidden');
    
    $('#show-visualization').click(function() {
        $('#filter').css('display', 'none');
        $('#result-tab-content').css('display', 'none');
        $('#visualization-tab-content').css('visibility', 'visible');
        $('#show-visualization').parent().addClass('active');
        $('#show-results').parent().removeClass('active');
    });

    $('#show-results').click(function() {
        $('#filter').css('display', 'none');
        $('#visualization-tab-content').css('visibility', 'hidden');
        $('#result-tab-content').css('display', 'inline');
        $('#show-results').parent().addClass('active');
        $('#show-visualization').parent().removeClass('active');
    });

    $('#show-filters').click(function() {
        $('#visualization-tab-content').css('visibility', 'hidden');
        $('#result-tab-content').css('display', 'inline');
        $('#show-results').parent().addClass('active');
        $('#show-visualization').parent().removeClass('active');
    });

    $('#show-filters').click( function() {
        $("#filter").toggle();
    });
});
