from src.static_features import *


class HTMLExtractor(FeatureExtractor):

    def calculate_score(self):
        raise NotImplementedError(
            "HTMLExtractor: Subclasses must implement this method"
        )
