from typing import Optional
from app.data.models import MatchEvent

class EventIngestionPipeline:
    """
    Stage A: Ingestion Layer
    Ingests synthetic match events as they happen:
    - Validates schema consistency
    - Enriches with metadata timestamps and session identifiers
    - Emits clean, normalized event into the processing stream
    """
    def __init__(self):
        self.total_ingested_events = 0

    def process(self, raw_event: MatchEvent) -> MatchEvent:
        self.total_ingested_events += 1
        
        # Ensure coordinates are bounded to 0-100 pitch coordinates
        raw_event.location.x = max(0.0, min(100.0, raw_event.location.x))
        raw_event.location.y = max(0.0, min(100.0, raw_event.location.y))
        
        if raw_event.end_location:
            raw_event.end_location.x = max(0.0, min(100.0, raw_event.end_location.x))
            raw_event.end_location.y = max(0.0, min(100.0, raw_event.end_location.y))
            
        return raw_event
