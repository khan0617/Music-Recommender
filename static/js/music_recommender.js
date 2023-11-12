// Initiate a searchSong request when the user hits Enter
document.getElementById('searchInput').addEventListener('keydown', (event) => {
    if (event.code === 'Enter') {
        console.log("we got an enter!");
        event.preventDefault();
        // Call searchSong function with the input's value if it's non-empty
        let inputVal = event.target.value;
        if (inputVal.trim()) {
            console.log(`Truthy input value! ${inputVal}`);
            searchSong(inputVal);
        }
    }
});

// initiate a searchSong request for the specified song.
function searchSong(songQuery) {
    if (songQuery) {
        fetch('/searchSong?query=' + encodeURIComponent(songQuery))
            .then(response => response.json())  // Parse the JSON response
            .then(data => {
                // Log the search results to the console
                console.log('Search results:', data);
            })
            .catch(error => console.error('Error searching song:', error));
    }
}


// Handles the selection of an autocomplete suggestion
// on click of a suggestion, initiate a searchSong() request.
function selectSuggestion(suggestion) {
    document.getElementById('searchInput').value = suggestion;
    clearSuggestions();
    searchSong(suggestion);  // Trigger the search when a suggestion is clicked
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