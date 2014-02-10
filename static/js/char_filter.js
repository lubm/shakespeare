//TODO(luciana): when selection is any, come back to only any in chars
function populateChars(data){
    chars = data['chars'];
    for (var i = 0; i < chars.length; i++) {
        $('#char-select').append(new Option(chars[i]));
    }
}

$(document).ready(function() {
    $('#work-select').change(function() {
        work = $(this).find(':selected').text();
        console.log(work);

        if (work == 'Any') {
            $('#char-select').empty();
            $('#char-select').append(new Option('Any'));
            return;
        }

        var request = {
            work_filter: work,
            searched_word: $('#search-value').val()
        };

        $.get('/chars', request, populateChars)
    });
});

function displayResults(data) {
    result = data['result'];
    console.log(result);
    $('#results').hide();
    $('#results').empty();
    if (result.length == 0) {
        message = document.createElement('p');
        $(message).text('No results found for ');
        word = document.createElement('i');
        $(word).text($('#search-value').val());
        $(message).append(word);
        $('#results').append(message);
    }
    for (work in result) {
        item = document.createElement('div');
        $(item).addClass('result-item');
        title = document.createElement('div');
        $(title).addClass('title text-danger');
        $(title).text(work);
        $(item).append(title);
        for (charac in result[work]) {
            speaker = document.createElement('p');
            $(speaker).addClass('leader');
            $(speaker).css('color', '#ccc');
            $(speaker).text(charac);
            $(item).append(speaker);
            for (var i = 0; i < result[work][charac].length; i++) {
                line = document.createElement('p');
                $(line).addClass('result-line');
                $(line).html(result[work][charac][i]);
                $(item).append(line);
            }
        }
        $('#results').append(item);
    }
    $('#results').show();
}

function filterByWorkAndCharacter() {
    var request = {
        char_filter: $('#char-select').find(':selected').text(),
        work_filter: $('#work-select').find(':selected').text(),
        searched_word: $('#search-value').val()
    };

    $.get('/filter', request, displayResults);
}
