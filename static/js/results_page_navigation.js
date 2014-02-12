$(window).load(function() {
    $('#visualization-tab-content').css('visibility', 'hidden');
    
    $('#show-visualization').click(function() {
        $('#result-tab-content').css('display', 'none');
        $('#visualization-tab-content').css('visibility', 'visible');
        $('#show-visualization').parent().addClass('active');
        $('#show-results').parent().removeClass('active');
    });

    $('#show-results').click(function() {
        $('#visualization-tab-content').css('visibility', 'hidden');
        $('#result-tab-content').css('display', 'inline');
        $('#show-results').parent().addClass('active');
        $('#show-visualization').parent().removeClass('active');
    });

    $('#show-filters').hover(
        function() {
            $(this).addClass('btn-no-padding');
        }, 
        function () {
            $(this).removeClass('btn-no-padding');
        }
    );
});
