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

$(document).ready(function() {
    $('#search-header').submit(function(event) {
        console.log('Here');
        event.preventDefault();

        var request = {
            char_filter: 'Any',
            work_filter: 'Any',
            searched_word: $('#search-value').val()
        };

        console.log($('#search-value').val());

        // TODO(all): how are we going to arrange the filter and search,
        // together or separated?
        $.get('/filter', request, displayResults)

    });

    $('#search-header').submit();
});
