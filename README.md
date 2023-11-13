# Music-Recommender
### A similar song finder using KNearestNeighbors, Flask, the Spotify API, and CUDA acceleration.
A web-interface to search for songs you like, and get up to 5 recommendations. The application forwards your search to Spotify, then uses a custom KNearestNeighbors classifier to retrieve the most similar songs from a local dataset of ~170,000 songs. The recommendations are not constrained to be the same genre as the query.

![Song Recommender](./music_recommender_screenshot.png)

# Before Starting
Important notes:
1. The system was test developed and tested using python 3.11 on Windows.
2. You will need to provide your own Spotify API login credentials
    - Go to https://developer.spotify.com/documentation/web-api, and get your `client_id` and `client_secret`. You can set the redirect url to `http://localhost/`
    - Create `spotify_credentials.txt` in the same folder as `spotify_manager.py`. The file should be a single line formatted as such: `client_id client_secret` (separated by a space). `SpotifyManager` reads these and loads them into `os.environ`.

# Usage
1. Install dependencies for the flask app and jupyter notebook: `pip install -r requirements.txt`
2. Launch the Flask app on localhost:5000: `python song_recommender_app.py` (you may need to use `python3` depending on your install).
    - Application logs are generated in `app.log` in the same directory as`song_recommender_app.py`.
3. Go to https://localhost:5000 in the browser. You should be able to search now!

# Files
- `data/`: Stores all `.csv` for the local database. The main one is `data.csv`.
- `static/`, `templates/`: Store css/js/image files and html templates respectively. Part of Flask's file hierarchy. 
- `app.log`: Application logging, created and appended to while running the app (not in the repo).
- `logging_config.py`: Ensures all files have the same logging configuration.
- `my_k_neighbors_classifier.py`: Implements KNN from scratch via `class MyKNeighborsClassifier`, allowing either euclidean of manhattan distance metrics.
- `recommendations_manager.py`: Implements `class RecommendationsManager`, responsible for taking a query from the user and resolving its recommendations.
- `requirements.txt`: Necessary dependencies to run the flask app and the jupyter notebook.
- `song_recommender_app.py`: The main flask app. Uses the flask development server to server the application to https://localhost:5000. Prints debug information to the terminal too.
- `song_recommender_exploration.ipynb`: Exploration of the music dataset. Provides visualizations to understand the data, and tests out various KNN implementations. Useful for seeing how different algorithms or distance metrics can provide different recommendations.
- `trie.py`: Implements a custom Trie datastructure to implement autocomplete on the web interface. The Trie is loaded with the song names from `data.csv`.