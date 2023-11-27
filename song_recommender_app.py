import pandas as pd
from numba import cuda
from flask import Flask, render_template, jsonify, request
from logging_config import setup_logging
from trie import Trie
from spotify_manager import SpotifyManager
from song import Song
from recommendations_manager import RecommendationsManager, DATA_FEATURES

data: pd.DataFrame
trie: Trie
spotify_manager: SpotifyManager
recommendations_manager: RecommendationsManager
app = Flask(__name__)
print('Music Recommender Flask App Started')
app.logger.info('Music Recommender Flask App Started')

def init() -> None:
    global data, trie, spotify_manager, recommendations_manager
    setup_logging()
    print('**Initializing**')
    print('Reading data.csv...', end='')
    data = pd.read_csv('./data/data.csv')
    print('Done.\nInitializing trie...', end='')
    trie = Trie.from_list_of_names(data[['name', 'artists']])
    print('Done.\nInitializing spotify_manager...', end='')
    spotify_manager = SpotifyManager()

    # TODO: create model type enum or baseclass to prevent hard-coded strings
    classifier = 'gpu_knn' if cuda.is_available() else 'knn'
    print(f'Done.\nInitializing recommendations_manager({classifier=})...', end='')
    recommendations_manager = RecommendationsManager(
        data=data, 
        features=DATA_FEATURES, 
        spotify_manager=spotify_manager,
        classifier=classifier
    )
    print('Done. Good to go!')

@app.route('/')
def home():
    cuda_available = cuda.is_available()
    return render_template('index.html', cuda_available=cuda_available)

@app.route('/autocomplete')
def autocomplete() -> str:
    """
    Provide 5 autocomplete results for a given autocomplete prefix.
    If prefix is an empty string, return no suggestions.
    Returns an html response to the client.
    """
    prefix = request.args.get('prefix', '')
    if prefix:
        autocomplete_results = trie.get_autocomplete_suggestions(prefix=prefix, limit=5)
    else:
        autocomplete_results = []
    app.logger.info(f'autocomplete({prefix=}): autocomplete_results: {autocomplete_results}')
    return render_template('autocomplete.html', suggestions=autocomplete_results)

@app.route('/recommendations')
def recommendations():
    """
    Return the search recommendations for this song, as an html string.
    Returns empty html string if we don't get any results.
    An example GET request could look like:
        "/recommendations?query=your_song_name&gpuEnabled=true&fromAutocomplete=false
    """
    query = request.args.get('query', '')
    artist_name = None
    from_autocomplete = request.args.get('fromAutocomplete', 'false') == 'true'
    gpu_enabled = request.args.get('gpuEnabled', 'false') == 'true'

    # TODO: create an enum or something so we don't have to use strings here
    if gpu_enabled and recommendations_manager.classifier != 'gpu_knn':
        recommendations_manager.classifier = 'gpu_knn'

    # if the request was made with autocomplete, we know the input will be: '{song_name} by {artist}'
    if from_autocomplete:
        query, artist_name = query.rsplit('by', 1)

    print(f'recommendations({query=}, {artist_name=}, {gpu_enabled=}) called!')

    if query and (song := spotify_manager.search_song(song_name=query, artist_name=artist_name)):
        recommendations: list[Song] = recommendations_manager.get_recommendations(song, num_recommendations=10)[:5]
        app.logger.info(f'recommendations({query=}, {artist_name=}, {gpu_enabled=}), found {len(recommendations)} recommendations!')
        return render_template('recommendations.html', main_song=song, recommendations=recommendations)
    
    app.logger.info(f'recommendations({query=}, {artist_name=}, {gpu_enabled=}), found no recommendations.')
    return render_template('recommendations.html', main_song=None, recommendations=[])

if __name__ == '__main__':
    init()
    app.run(debug=False)