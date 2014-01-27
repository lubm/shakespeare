$(document).ready(function(){
	var disable = true;
	if ($('#search-value').val().length > 0) {
		disable = false;
	};
    $('#search-button').attr('disabled', disable);
    
    $('#search-value').keyup(function(){
        if($(this).val().length > 0){
            disabled = false
        } else {
        	disabled = true
        }
       	$('#search-button').attr('disabled', disabled);
    })
});