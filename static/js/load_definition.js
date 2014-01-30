var shakespy = {};

$(document).ready(function(){
	var request = {
		searched_word: $('#search-value').val()
	};

	$.get( "/define", request, function( wordDefinition ) {
		$('#loading_message').remove();
		$('#definition').append(wordDefinition);
	});
});
