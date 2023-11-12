import json
import pandas as pd
from flask import Flask, render_template, jsonify, request
from logging_config import setup_logging
from trie import Trie
from spotify_manager import SpotifyManager

setup_logging()
data = pd.read_csv('./data/data.csv')
trie = Trie.from_list_of_names(data[['name', 'artists']])
spotify_manager = SpotifyManager()
app = Flask(__name__)
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
    if query and (song := spotify_manager.search_song(query)):
        response = song.to_dict()
    app.logger.info(f'search_song({query=}), response = {json.dumps(response, indent=4)}')
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
