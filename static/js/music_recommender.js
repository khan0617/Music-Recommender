// Adjust the autocomplete suggestions' width on page load and window resize
window.addEventListener('load', adjustSuggestionsWidth);
window.addEventListener('resize', adjustSuggestionsWidth);

// Initiate a getRecommendations request when the user hits Enter
document.getElementById('searchInput').addEventListener('keydown', (event) => {
    if (event.code === 'Enter') {
        console.log("we got an enter!");
        event.preventDefault();
        // Call getRecommendations function with the input's value if it's non-empty
        let inputVal = event.target.value;
        if (inputVal.trim()) {
            console.log(`Truthy input value! ${inputVal}`);
            getRecommendations(inputVal);
        }
    }
});

// zero-out the suggestions when input loses focus.
document.getElementById('searchInput').addEventListener('focusout', (event) => {
    // there needs to be a delay before we clear the suggestions, because
    // clicking on a suggestion technically counts as 'focusout'.
    // so give time for the GET /recommendations to get sent before clearing them.
    setTimeout(() => {
        if (!document.getElementById('searchInput').matches(':focus')) {
            clearSuggestions();
        }
    }, 100); // Adjust the delay as needed
});

// let autocomplete suggestions area scale dynamically with the search bar and page
function adjustSuggestionsWidth() {
    let inputWidth = document.getElementById('searchInput').offsetWidth;
    let suggestionsContainer = document.getElementById('suggestionsContainer');
    suggestionsContainer.style.width = inputWidth + 48 + 'px';
}

// initiate a getRecommendations request for the specified song.
/**
 * @param {string} songQuery - The query, like 'Forever Young by BLACKPINK'.
 * @param {boolean} fromAutocomplete - let the backend know we are looking for a recommendation that is part of the database
 */
function getRecommendations(songQuery, fromAutocomplete = false) {
    if (songQuery) {
        console.log(`Called getRecommendations(songQuery=${songQuery}, fromAutocomplete=${fromAutocomplete})!`);
        let url = '/recommendations?query=' + encodeURIComponent(songQuery);
        if (fromAutocomplete) {
            url += '&fromAutocomplete=true';
        }

        fetch(url)
            .then(response => response.text())  // Parse the response as text (HTML)
            .then(html => {
                // Insert the HTML into the recommendations section of the page
                document.getElementById('recommendations').innerHTML = html;
            })
            .catch(error => console.error('Error searching song:', error));
    }
}


// Handles the selection of an autocomplete suggestion
// on click of a suggestion, initiate a getRecommendations() request.
function selectSuggestion(suggestion) {
    document.getElementById('searchInput').value = suggestion;
    clearSuggestions();
    getRecommendations(suggestion, fromAutocomplete=true);  // Trigger the search when a suggestion is clicked
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