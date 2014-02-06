/* This module handles forms interaction in the admin page. It was inpired by
 * the file custom.js available in the Map Reduce library. */

function updateForm(filekey, blobkey, filename) {
    /* Updates the form to contains the information regarding a radio button
     * selected. It is used to allow this data to be submitted. */
    $('#jobName').val(filename);
    $('#filekey').val(filekey);
    $('#blobkey').val(blobkey);
    $('#index').attr('disabled', false);
}

$(document).ready(function(){
    /* Submits the selected file to be indexed. */
    $('#index-form').submit(function(event) {

        event.preventDefault();

        data = {
            'filename': $('#jobName').val(), 
            'filekey': $('#filekey').val(),
            'blobkey': $('#blobkey').val()
        };

        $.post(
            '/admin',
            data,
            function() {
                $('#index-message').css('display', 'inline');
            },
            'json'
        ).always(function() {
            $('#index-message').css('display', 'inline');
        });
    });

    /* Upload the inserted file if it's extension is zip. */
    $('#upload-form').submit(function(event) {
        if ($('#file').val().match(/.zip$/)) {
            $('#update-error').css('display', 'none');
            $('#update-loading').css('display', 'inline');
        } else {
            $('#update-error').css('display', 'inline');
            event.preventDefault();
        }    
    });

});

function displayClearLoading() {
    /* Display loading while cleaning the database. */
    $('#clear-loading').css('display', 'inline');
}
