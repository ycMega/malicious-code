from src.static_features import *


class URLExtractor(FeatureExtractor):

    def extract(self):
        raise NotImplementedError("URLExctactor: Subclasses must implement this method")
