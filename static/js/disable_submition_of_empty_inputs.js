$(document).ready(function(){
	var disable = true;
	if ($('.non-nulleable-input').val().length > 0) {
		disable = false;
	}
    $('.disabled-when-input-is-null-button').attr('disabled', disable);

    $('.non-nulleable-input').keyup(function(){
        disabled = ($(this).val().length > 0) ? false : true;
       	$('.disabled-when-input-is-null-button').attr('disabled', disabled);
    });
});