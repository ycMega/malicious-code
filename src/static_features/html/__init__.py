from src.static_features import *


class HTMLExtractor(FeatureExtractor):

    def extract(self):
        raise NotImplementedError(
            "HTMLExtractor: Subclasses must implement this method"
        )
