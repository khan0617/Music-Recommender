import json
import pandas as pd
from flask import Flask, render_template, jsonify, request
from logging_config import setup_logging
from trie import Trie
from spotify_manager import SpotifyManager

setup_logging()
print('**Initializing**')
data = pd.read_csv('./data/data.csv')
print('Finished reading data.csv')
trie = Trie.from_list_of_names(data[['name', 'artists']])
print('Initialized trie')
spotify_manager = SpotifyManager()
print('Initialized spotify_manager')
app = Flask(__name__)
print('Music Recommender Flask App Started')
app.logger.info('Music Recommender Flask App Started')

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/searchSong')
def search_song():
    """
    Return the search results for this song, as a json response.
    Returns empty dict on failure to get results.
    """
    response = {}
    query = request.args.get('query', '')
    artist_name = None
    from_autocomplete = request.args.get('fromAutocomplete', 'false') == 'true'

    # if the request was made with autocomplete, we know the input will be: '{song_name} by {artist}'
    if from_autocomplete:
        query, artist_name = query.rsplit('by', 1)

    if query and (song := spotify_manager.search_song(song_name=query, artist_name=artist_name)):
        response = song.to_dict()

    msg = f'search_song({query=}, {from_autocomplete=} {artist_name=}), response = {json.dumps(response, indent=4)}'
    print(msg)
    app.logger.info(msg)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
