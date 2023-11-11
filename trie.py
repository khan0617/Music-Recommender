# trie.py implements a Trie datastructure to store all the song names.
# this allows us to provide a sort of autocomplete in the web interface.
from __future__ import annotations
import logging
import pandas as pd
import numpy as np
from sklearn.utils import shuffle
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end_of_word = False
        self.original_words = []  # original words with capitalization etc

class Trie:
    """A Trie data structure for efficient prefix-based searching."""
    def __init__(self) -> None:
        self.root = TrieNode()

    @classmethod
    def from_list_of_names(cls, song_names: pd.DataFrame | pd.Series, sample_frac: float | None = None) -> Trie:
        """
        Create and initialize a Trie using a dataframe of a list of song names.
        Randomly sample a percentage of names if we don't want a Trie of 170,000 items.
        """
        trie = cls()
        # sample a fraction of the names to help save memory
        if sample_frac is not None:
            song_names = song_names.sample(frac=sample_frac)

        # randomize the insertions into the tree for more interesting search results
        song_names = song_names.sample(frac=1).reset_index(drop=True)

        for song_name in song_names:
            trie.insert(str(song_name))

        logging.info(f'Created Trie, inserted {len(song_names)} song names')
        return trie

    def insert(self, word: str) -> None:
        """
        Insert this word into the Trie.
        """
        node = self.root
        for char in word.lower(): # use lowercase chars as keys in the children
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        if word not in node.original_words: # here we store the words with proper capitalization
            node.original_words.append(word)

    def _search(self, node: TrieNode, limit: int, suggestions: list[str]) -> None:
        """
        Recursively search for autocomplete suggestions based on the given prefix.

        Args:
            node (TrieNode): The current node in the Trie.
            prefix (str): The current prefix formed by traversing the Trie.
            limit (int): The maximum number of suggestions to return.
            suggestions (list[str]): The list to store suggestions.
        """
        if len(suggestions) >= limit:
            return
        
        if node.is_end_of_word:
            suggestions.extend(node.original_words[:limit - len(suggestions)])

        for char, next_node in node.children.items():
            self._search(next_node, limit, suggestions)
    
    def get_autocomplete_suggestions(self, prefix: str, limit: int = 5) -> list[str]:
        """
        Get autocomplete suggestions for a given prefix.

        Args:
            prefix (str): The prefix to search for in the Trie.
            limit (int): The maximum number of autocomplete suggestions to return.

        Returns:
            list[str]: A list of autocomplete suggestions.
        """
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        
        suggestions = []    
        self._search(node, limit, suggestions)
        return suggestions
    
# test out the Trie
if __name__ == '__main__':
    df = pd.read_csv('./data/data.csv')
    trie = Trie.from_list_of_names(df['name'])
    print(f'{trie.get_autocomplete_suggestions("lovesick") = }')
