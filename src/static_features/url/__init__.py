from src.static_features import *


class URLExtractor(FeatureExtractor):

    def calculate_score(self):
        raise NotImplementedError("URLExctactor: Subclasses must implement this method")
