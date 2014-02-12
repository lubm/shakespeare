/* This module regards the client operations and requests in the
 * results page. It is responsible for tetching the results in the server and
 * rendering on the html, besides responding to interaction in the filter
 * form. */

function getSearchedWord() {
    /* We get the searched word from the query paramaters in order to avoid the
    situation in which the user changes the searched word without pressing the
    button */
    return document.location.search.split('=')[1]; 
}

function insertMentions(mentions) {
    /* Displays the mentions of the search filtered by work and character. The 
     * filter is optional */
    if (jQuery.isEmptyObject(mentions)) {
        message = document.createElement('p');
        $(message).text('No results found for ');
        word = document.createElement('i');
        $(word).text($('#search-value').val());
        $(message).append(word);
        $(message).addClass('harlem-shake');
        $(message).attr('data-animation', 'wobble');
        $('#results').append(message);
    }
    
    for (work in mentions) {
        item = document.createElement('div');
        $(item).addClass('result-item');
        title = document.createElement('div');
        $(title).addClass('title text-danger');
        $(title).text(work);
        $(title).addClass('harlem-shake');
        $(title).attr('data-animation', 'tada');
        $(item).append(title);


        characterMentions = document.createElement('div');
        $(characterMentions).addClass('character-mentions');

        for (charac in mentions[work]) {
            speaker = document.createElement('p');
            $(speaker).addClass('leader');
            $(speaker).css('color', '#ccc');
            $(speaker).text(charac);
            $(speaker).addClass('harlem-shake');
            $(speaker).attr('data-animation', 'scale');
            $(characterMentions).append(speaker);

            characterLines = document.createElement('div');
            $(characterLines).addClass('character-lines');

            var mentions_length = mentions[work][charac].length;
            for (var i = 0; i < mentions_length; i++) {
                line = document.createElement('p');
                $(line).addClass('result-line');
                $(line).html(mentions[work][charac][i]);
                if (i > 4) {
                    $(line).hide();
                }
                $(characterLines).append(line);
            }
            if(mentions_length > 4) {
                load_more = document.createElement('a');
                $(load_more).addClass('load_more');
                $(load_more).attr('character', charac);
                $(load_more).attr('work', work);
                $(load_more).text("Load " + (mentions_length-4-1) + " more lines");
                $(characterLines).append(load_more);
            }

            $(characterMentions).append(characterLines);

        }
        $(item).append(characterMentions);
        $('#results').append(item);
    }
}

function insertResultsInfo(time, number_results, number_works) {
    /* Insert the time metrics and the number of results to the html */
    $('#results-info').text(
        number_results + " results in  " + number_works + " works (" + 
        time + " seconds)");   
}

function insertDidYouMean(did_you_mean) {
    /* If there is a suggestion for the not found word, this function inserts it
    to the html */
    if (did_you_mean) {
        $('#did-you-mean-sugg').attr('href', '/results?searched_word=' + 
            did_you_mean);
        $('#did-you-mean-sugg').text(did_you_mean);
        $('#did-you-mean').show();
    }
}

function insertResults(result) {
    /* Insert all the request results in the html */
    
    mentions = result['mentions'];
    console.log(mentions);
    insertMentions(mentions);

    time = result['time'];
    number_results = result['number_results'];
    insertResultsInfo(time, number_results, Object.keys(mentions).length);

    did_you_mean = result['did_you_mean'];
    insertDidYouMean(did_you_mean); 
}

function populateChars(data){
    /* Insert the characters in the select element for the filter, according to
     * the work selected */ 
    chars = data['chars'];
    $('#char-select').empty();
    $('#char-select').append(new Option('Any'));
    for (var i = 0; i < chars.length; i++) {
        $('#char-select').append(new Option(chars[i]));
    }
}

function populateWorks(data){
    /* Insert the works in the select element for the filter, according to
     * the search word */ 
    works = data['works'];
    $('#work-select').empty();
    $('#work-select').append(new Option('Any'));
    for (var i = 0; i < works.length; i++) {
        $('#work-select').append(new Option(works[i]));
    }
}

function resultsLoadingStart() {
    /* Show a loding icon while the results are being retrieved */
    $('#results').hide();
    $('#results').empty();
    $('#results-loading').show();
}

function resultsLoadingFinish() {
    $('#results-loading').hide();
    $('#results').show();
    generateLoadMoreHandlers();
}

function treemapLoadingStart() {
    $('#treemap-loading').show();
}

function treemapLoadingFinish() {
    $('#treemap-loading').hide();
}

$(document).ready(function() {
    $('#work-select').change(function() {
        /* When the user changes the work the list of characters needs to be 
        reloaded.
        We call changed in order to change the value of the character and
        therefore trigger the query to the server. */
        $('#char-select').val('Any').change();
    });

    $('#char-select').change(function() {
        filterByWorkAndCharacter();
    });
});

function filterByWorkAndCharacter() {
    /* Filter the results of the searched word according to work and character.
     * It does not change the treemap since it is associated only to the word.
     * */
    resultsLoadingStart()

    var request = {
        char_filter: $('#char-select').find(':selected').text(),
        work_filter: $('#work-select').find(':selected').text(),
        searched_word: getSearchedWord() 
    };

    $.get('/search', request, function(result) {
        insertResults(result);
        resultsLoadingFinish();
    });

}


function generateLoadMoreHandlers() {
    /* For each Load More link, this functions add a click handler for managing
    the pagination.

    We need to call this when the elements are already uploaded to the DOM. 
    That's why we are calling this function here, after the insertRestults
    method. */
    $('.load_more').click(function() {
        $(this).parent().children().fadeIn();
        $(this).hide();
    });
}

function loadTreemap() {
    /* Make a request to load the treemap regarding the searched word */
    
    var request = {
        searched_word: $('#search-value').val()
    };
    
    $.get('/treemap', request, function(data) {
        drawChart(data);
        treemapLoadingFinish();
    });

}


$(document).ready(function() {
    $('#search-button').click(function() {
        /* This changes the url when the submit button is clicked and then the
         * submit is placed because of the reload of the page. To prevent the 
         * reload we would have to use a plugin, which we did not want include 
         * for only this purpose. */
        document.location.replace('?searched_word=' + $('#search-value').val()); 
    });

    $('#search-header').submit(function(event) {
        /* Submit the search word with optional filter arguments */
        event.preventDefault();

        resultsLoadingStart();
        treemapLoadingStart();

        var request = {
            char_filter: 'Any',
            work_filter: 'Any',
            searched_word: getSearchedWord() 
        };

        $.get('/search', request, function(result) {
            insertResults(result);
            resultsLoadingFinish();
        });

        $.get('/works', request, populateWorks);

        loadTreemap();

    });

    /* The submit is placed at every page reload */
    $('#search-header').submit();

    $('#work-select').change(function() {
        /* Update the character information int the filter according to the work
         * selected */
        work = $(this).find(':selected').text();

        if (work == 'Any') {
            $('#char-select').empty();
            $('#char-select').append(new Option('Any'));
            return;
        };

        var request = {
            work_filter: work,
            searched_word: $('#search-value').val()
        };

        $.get('/chars', request, populateChars);
    });
});
