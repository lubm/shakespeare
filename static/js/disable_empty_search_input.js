$(document).ready(function(){
	var disable = true;
	if ($('#search-value').val().length > 0) {
		disable = false;
	}
    $('#search-button').attr('disabled', disable);

    $('#search-value').keyup(function(){
        disabled = ($(this).val().length > 0) ? false : true;
       	$('#search-button').attr('disabled', disabled);
    });
});