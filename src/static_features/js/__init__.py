from src.static_features import *


class JSExtractor(FeatureExtractor):

    def calculate_score(self):
        raise NotImplementedError("JSExctactor: Subclasses must implement this method")
