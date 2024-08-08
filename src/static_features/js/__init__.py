from src.static_features import *


class JSExtractor(FeatureExtractor):

    def extract(self):
        raise NotImplementedError("JSExctactor: Subclasses must implement this method")
