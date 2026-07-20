from openai import OpenAI
from regulatory_compliance.core.config import settings
 
 
class EmbeddingService:
    """
    Generates embeddings using OpenAI.
    """