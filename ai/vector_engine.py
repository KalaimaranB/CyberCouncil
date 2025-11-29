"""
Vector embedding engine using PyTorch and sentence transformers.

This module provides a PyTorch-based text embedding engine that converts
text into 384-dimensional vectors for semantic similarity search. It uses
the 'all-MiniLM-L6-v2' sentence transformer model and supports Apple Silicon
(MPS) hardware acceleration for faster processing.

Key Features:
- Converts text to semantic vectors (embeddings)
- Apple Silicon GPU acceleration (MPS)
- LangChain-compatible interface
- Batch processing for efficiency

Typical Usage:
    embedder = PyTorchEmbedder()
    vectors = embedder.embed_documents(["text1", "text2"])
    query_vector = embedder.embed_query("search query")
"""

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List

# Model configuration
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 produces 384-dimensional vectors


class PyTorchEmbedder:
    """
    PyTorch-based text embedding engine for semantic similarity search.
    
    Converts text strings into 384-dimensional vectors using the
    'all-MiniLM-L6-v2' sentence transformer model. Supports Apple Silicon
    (MPS) acceleration for improved performance.
    
    Attributes:
        device: torch.device - GPU (MPS) or CPU device
        tokenizer: AutoTokenizer - Text tokenizer
        model: AutoModel - Pre-trained transformer model
    """
    
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding engine.
        
        Args:
            model_name: Hugging Face model identifier (default: all-MiniLM-L6-v2)
        """
        print(f"⚡ [Engine] Initializing PyTorch Model: {model_name}")
        
        # Check for Apple Silicon (MPS) acceleration
        if torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("   -> 🚀 Hardware Acceleration: ENABLED (Apple Metal)")
        else:
            self.device = torch.device("cpu")
            print("   -> ⚠️ Hardware Acceleration: DISABLED (Running on CPU)")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)

    def _mean_pooling(self, model_output, attention_mask):
        """
        Apply mean pooling to token embeddings to get sentence embeddings.
        
        Averages all token vectors (weighted by attention mask) to produce
        a single vector representing the entire sentence.
        
        Args:
            model_output: Model output containing token embeddings
            attention_mask: Mask indicating which tokens to include
            
        Returns:
            torch.Tensor: Pooled sentence embeddings
        """
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Convert multiple text documents into vector embeddings (batch processing).
        
        LangChain-compatible method for embedding multiple documents efficiently.
        Processes all texts in a single batch for better performance.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of 384 floats)
            
        Raises:
            ValueError: If texts is empty
            TypeError: If texts contains non-string elements
        """
        # Input validation
        if not texts:
            raise ValueError("texts cannot be empty")
        if not all(isinstance(t, str) for t in texts):
            raise TypeError("All elements in texts must be strings")
        
        # Tokenize
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        encoded_input = {k: v.to(self.device) for k, v in encoded_input.items()}

        # Compute embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input)

        # Pool & Convert
        sentence_embeddings = self._mean_pooling(model_output, encoded_input['attention_mask'])
        
        # Return as list of floats (CPU-side)
        return sentence_embeddings.cpu().numpy().tolist()

    def embed_query(self, text: str) -> List[float]:
        """
        Convert a single text query into a vector embedding.
        
        LangChain-compatible method for embedding a single query string.
        This is a convenience wrapper around embed_documents().
        
        Args:
            text: Text string to embed
            
        Returns:
            Embedding vector (list of 384 floats)
            
        Raises:
            TypeError: If text is not a string
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        
        return self.embed_documents([text])[0]
