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

// add an event listener for the GPU toggle switch
document.addEventListener('DOMContentLoaded', function() {
    let gpuToggle = document.getElementById('gpuToggle');
    gpuToggle.addEventListener('change', function() {
        handleGPUToggle(gpuToggle);
    });
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
    }, 200);
});

/**
 * Update the gpu toggle text depending on the user's selection
 * @param {HTMLElement} gpuToggle: The toggle switch element controlling GPU usage.
 */
function handleGPUToggle(gpuToggle) {
    let label = document.querySelector('label[for="gpuToggle"]');
    label.textContent = gpuToggle.checked ? 'GPU Enabled' : 'GPU Disabled';
}

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
        let gpuEnabled = document.getElementById('gpuToggle').checked; // Get the state of the GPU toggle
        let url = '/recommendations?query=' + encodeURIComponent(songQuery) + '&gpuEnabled=' + gpuEnabled;
        if (fromAutocomplete) {
            url += '&fromAutocomplete=true';
        }
        letUserKnowWeAreSearchingForRecs();
        fetch(url)
            .then(response => response.text())  // Parse the response as text (HTML)
            .then(html => {
                // Insert the HTML into the recommendations section of the page
                document.getElementById('recommendations').innerHTML = html;
            })
            .catch(error => console.error('Error searching song:', error));
    }
}

// let the user know we're searching for recommendations.
function letUserKnowWeAreSearchingForRecs() {
    document.getElementById('recommendations').innerHTML = `<div class="default-text-header">Finding your recommendations...</div>`;
}

function clearRecommendations() {
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.classList.add('fade-out');

    // Clear content after the fade-out animation duration (500 ms here)
    setTimeout(() => {
        recommendationsDiv.innerHTML = 
            `
            <svg class="mb-3" xmlns="http://www.w3.org/2000/svg" height="72" viewBox="0 -960 960 960" width="72" fill="white">
                <path d="M400-120q-66 0-113-47t-47-113q0-66 47-113t113-47q23 0 42.5 5.5T480-418v-422h240v160H560v400q0 66-47 113t-113 47Z"/>
            </svg>
            <div class="default-text-header">Similar songs will appear here for you</div>
            <div class="default-text-footer">Get started by searching for a song you like.</div>
            `;
        recommendationsDiv.classList.remove('fade-out'); // Remove the class to reset for next time
    }, 300); // Match this with the CSS animation duration

    document.getElementById('searchInput').value = '';
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