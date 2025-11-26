import dspy
from src.agent.fund_search.modules.intent import IntentClassifier
from src.agent.fund_search.modules.extraction import SpecializedExtractor

class FundExtractionPipeline(dspy.Module):
    """
    Wrapper module that chains IntentClassifier and SpecializedExtractor
    for end-to-end evaluation of the extraction phase.
    """
    def __init__(self):
        super().__init__()
        self.intent_classifier = IntentClassifier()
        self.extractor = SpecializedExtractor()

    def forward(self, query: str):
        # 1. Classify Intent
        intent_pred = self.intent_classifier(query=query)
        intents = intent_pred.intents
        search_query = intent_pred.search_query
        
        # 2. Extract Criteria
        extractor_pred = self.extractor(
            query=query,
            intents=intents,
            search_query=search_query
        )
        
        return dspy.Prediction(
            intents=intents,
            criteria=extractor_pred.parsed_query
        )

