import re
import time

from bs4 import BeautifulSoup
from typeguard import typechecked

from src.io.feature_extractor import (
    ExtractorMeta,
    FeatureExtractionResult,
    FeatureExtractor,
)
from src.io.file_extractor import WebData
