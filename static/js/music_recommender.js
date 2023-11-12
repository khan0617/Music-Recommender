// Handles the selection of an autocomplete suggestion
function selectSuggestion(suggestion) {
    document.getElementById('searchInput').value = suggestion;
    document.getElementById('suggestionsContainer').innerHTML = '';
}

// Fetches autocomplete suggestions for the search bar
function fetchAutocompleteSuggestions() {
    var inputVal = document.getElementById('searchInput').value;
    if (inputVal === '') {
        clearSuggestions();
        return;
    }
    // The server will return html we can insert directly into the DOM
    fetch('/autocomplete?prefix=' + encodeURIComponent(inputVal))
        .then(response => response.text())  // Expect a text (HTML) response
        .then(html => {
            document.getElementById('suggestionsContainer').innerHTML = html;
        })
        .catch(error => console.error('Error fetching autocomplete suggestions:', error));
}

// Clears the suggestions from the suggestions container
function clearSuggestions() {
    document.getElementById('suggestionsContainer').innerHTML = '';
}

// Displays suggestions in the suggestions container
function displaySuggestions(suggestions) {
    var suggestionsContainer = document.getElementById('suggestionsContainer');
    clearSuggestions();
    suggestions.forEach(suggestion => {
        var div = document.createElement('div');
        div.className = 'suggestion-item';
        div.innerText = suggestion;
        div.onclick = function() {
            selectSuggestion(suggestion);
        };
        suggestionsContainer.appendChild(div);
    });
}