from collections import Counter

from src.static_features import *
from src.utils.css import css_rules_listing, extract_css_features


class CSSExtractor(FeatureExtractor):

    def calculate_score(self):
        raise NotImplementedError(
            "HTMLExtractor: Subclasses must implement this method"
        )
