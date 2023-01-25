import json

from modules.constants import RATING_FILE


class Rating:
    def __init__(self):
        self.rating = dict()
        self.load_rating()

    def load_rating(self):
        with open(RATING_FILE, 'r') as f:
            self.rating = json.load(f)

    def add_result(self, name, score):
        self.rating[name] = score
        with open(RATING_FILE, 'w') as f:
            json.dump(self.rating, f)

    def get_sorted(self):
        return sorted(self.rating.items(), key=lambda x: -x[1])

