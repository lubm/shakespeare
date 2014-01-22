var shakespy = {};

window.onload = function() {
	shakespy.http = new XMLHttpRequest();

	shakespy.http.onreadystatechange = function() {

		if(shakespy.http.readyState == 4 && shakespy.http.status == 200) {
			var wordDefinition = shakespy.http.responseText;
			var definitionDiv = document.getElementById('definition');
			var loadingDefinitionDiv = document.getElementById('loading_message');
			var definitionDivContent = document.createTextNode(wordDefinition);
			definitionDiv.removeChild(loadingDefinitionDiv);
			definitionDiv.appendChild(definitionDivContent);
		}
	}

	shakespy.url = "/define";
	shakespy.searchedWord = document.getElementById('search-value').value;
	shakespy.http.open("GET", shakespy.url + "?searched_word=" + shakespy.searchedWord, true);
	shakespy.http.send(null);
};