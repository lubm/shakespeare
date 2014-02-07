$(window).load(function() {
    $('#show-visualization').click(function() {
    	$('#result-tab-content').hide();
  		$('#visualization-tab-content').show();
  		$('#show-visualization').parent().addClass('active');
  		$('#show-results').parent().removeClass('active');
	});

    $('#show-results').click(function() {
    	$('#visualization-tab-content').hide();
    	$('#result-tab-content').show();
    	$('#show-results').parent().addClass('active');
  		$('#show-visualization').parent().removeClass('active');
	});
});