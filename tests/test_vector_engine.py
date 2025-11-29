"""
Tests for Vector Engine module.
Tests embedding generation, input validation, and hardware acceleration.
"""

import pytest
import torch
from ai.vector_engine import PyTorchEmbedder, EMBEDDING_DIMENSION


class TestPyTorchEmbedder:
    """Test suite for PyTorchEmbedder class"""
    
    def test_init(self):
        """Test embedder initialization"""
        embedder = PyTorchEmbedder()
        
        assert embedder.tokenizer is not None
        assert embedder.model is not None
        assert embedder.device is not None
        
        # Device should be MPS or CPU
        assert embedder.device.type in ["mps", "cpu"]
    
    def test_embedding_dimension(self):
        """Test that embeddings have correct dimension"""
        embedder = PyTorchEmbedder()
        
        vector = embedder.embed_query("Test text")
        
        assert len(vector) == EMBEDDING_DIMENSION
        assert len(vector) == 384
    
    def test_embed_query_single_text(self):
        """Test embedding a single query"""
        embedder = PyTorchEmbedder()
        
        text = "Buffer overflow vulnerability"
        vector = embedder.embed_query(text)
        
        assert isinstance(vector, list)
        assert len(vector) == 384
        assert all(isinstance(v, float) for v in vector)
    
    def test_embed_documents_multiple_texts(self):
        """Test embedding multiple documents"""
        embedder = PyTorchEmbedder()
        
        texts = [
            "SMB vulnerability",
            "Linux kernel exploit",
            "Buffer overflow basics"
        ]
        
        vectors = embedder.embed_documents(texts)
        
        assert isinstance(vectors, list)
        assert len(vectors) == 3
        assert all(len(v) == 384 for v in vectors)
        assert all(isinstance(v, list) for v in vectors)
    
    def test_semantic_similarity(self):
        """Test that similar texts have similar embeddings"""
        embedder = PyTorchEmbedder()
        
        # Similar texts
        vec1 = embedder.embed_query("SMB vulnerability")
        vec2 = embedder.embed_query("SMB exploit")
        
        # Different text
        vec3 = embedder.embed_query("Linux kernel")
        
        # Compute cosine similarity (simple dot product for normalized vectors)
        import numpy as np
        
        # Normalize vectors
        v1 = np.array(vec1) / np.linalg.norm(vec1)
        v2 = np.array(vec2) / np.linalg.norm(vec2)
        v3 = np.array(vec3) / np.linalg.norm(vec3)
        
        similarity_12 = np.dot(v1, v2)
        similarity_13 = np.dot(v1, v3)
        
        # Similar texts should be more similar than different texts
        assert similarity_12 > similarity_13
    
    def test_embed_query_validation_non_string(self):
        """Test that embed_query raises TypeError for non-string input"""
        embedder = PyTorchEmbedder()
        
        with pytest.raises(TypeError, match="text must be a string"):
            embedder.embed_query(123)
        
        with pytest.raises(TypeError, match="text must be a string"):
            embedder.embed_query(None)
        
        with pytest.raises(TypeError, match="text must be a string"):
            embedder.embed_query(["list", "of", "strings"])
    
    def test_embed_documents_validation_empty_list(self):
        """Test that embed_documents raises ValueError for empty list"""
        embedder = PyTorchEmbedder()
        
        with pytest.raises(ValueError, match="texts cannot be empty"):
            embedder.embed_documents([])
    
    def test_embed_documents_validation_non_string_elements(self):
        """Test that embed_documents raises TypeError for non-string elements"""
        embedder = PyTorchEmbedder()
        
        with pytest.raises(TypeError, match="All elements in texts must be strings"):
            embedder.embed_documents(["valid", 123, "text"])
        
        with pytest.raises(TypeError, match="All elements in texts must be strings"):
            embedder.embed_documents([None, "text"])
    
    def test_embed_documents_single_element(self):
        """Test embedding a single document in a list"""
        embedder = PyTorchEmbedder()
        
        vectors = embedder.embed_documents(["Single text"])
        
        assert len(vectors) == 1
        assert len(vectors[0]) == 384
    
    def test_consistency(self):
        """Test that same text produces same embedding"""
        embedder = PyTorchEmbedder()
        
        text = "Test consistency"
        vec1 = embedder.embed_query(text)
        vec2 = embedder.embed_query(text)
        
        # Should be identical (or very close due to floating point)
        import numpy as np
        assert np.allclose(vec1, vec2, rtol=1e-5)
    
    def test_different_texts_different_embeddings(self):
        """Test that different texts produce different embeddings"""
        embedder = PyTorchEmbedder()
        
        vec1 = embedder.embed_query("First text")
        vec2 = embedder.embed_query("Second text")
        
        # Should be different
        assert vec1 != vec2
    
    def test_empty_string_handling(self):
        """Test handling of empty string"""
        embedder = PyTorchEmbedder()
        
        # Should not crash, but produce a valid embedding
        vector = embedder.embed_query("")
        
        assert isinstance(vector, list)
        assert len(vector) == 384
    
    def test_long_text_handling(self):
        """Test handling of very long text (truncation)"""
        embedder = PyTorchEmbedder()
        
        # Create a very long text (longer than model's max length)
        long_text = "word " * 1000
        
        # Should not crash, should truncate
        vector = embedder.embed_query(long_text)
        
        assert isinstance(vector, list)
        assert len(vector) == 384
    
    def test_special_characters(self):
        """Test handling of special characters"""
        embedder = PyTorchEmbedder()
        
        texts = [
            "Text with émojis 🚀",
            "Code: def foo():",
            "Math: x² + y² = z²",
            "Symbols: @#$%^&*()"
        ]
        
        vectors = embedder.embed_documents(texts)
        
        assert len(vectors) == 4
        assert all(len(v) == 384 for v in vectors)
    
    def test_batch_vs_single_consistency(self):
        """Test that batch and single embedding produce same results"""
        embedder = PyTorchEmbedder()
        
        text = "Test text"
        
        # Single embedding
        single_vec = embedder.embed_query(text)
        
        # Batch embedding
        batch_vec = embedder.embed_documents([text])[0]
        
        # Should be identical
        import numpy as np
        assert np.allclose(single_vec, batch_vec, rtol=1e-5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
