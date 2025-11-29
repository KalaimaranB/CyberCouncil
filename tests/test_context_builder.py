"""
Tests for Context Builder module.
Tests MMR retrieval, project context loading, and full context building.
"""

import pytest
import os
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from langchain_core.documents import Document
from core.context_builder import ContextBuilder


class TestContextBuilder:
    """Test suite for ContextBuilder class"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock ChromaDB instance"""
        return Mock()
    
    @pytest.fixture
    def builder(self, mock_db):
        """Create a ContextBuilder instance with mock DB"""
        return ContextBuilder(db=mock_db)
    
    def test_init(self, mock_db):
        """Test context builder initialization"""
        builder = ContextBuilder(db=mock_db)
        assert builder.db is mock_db
    
    def test_retrieve_with_mmr_basic(self, builder, mock_db):
        """Test basic MMR retrieval"""
        # Mock documents with scores
        doc1 = Document(page_content="test content 1", metadata={'title': 'Note 1'})
        doc2 = Document(page_content="test content 2", metadata={'title': 'Note 2'})
        
        mock_db.similarity_search_with_score.return_value = [
            (doc1, 0.9),
            (doc2, 0.8)
        ]
        
        results = builder.retrieve_with_mmr("test query", k=2)
        
        assert len(results) == 2
        assert doc1 in results
        assert doc2 in results
    
    def test_retrieve_with_mmr_filters_by_threshold(self, builder, mock_db):
        """Test MMR filters out low-relevance documents"""
        doc1 = Document(page_content="relevant content", metadata={'title': 'Note 1'})
        doc2 = Document(page_content="irrelevant content", metadata={'title': 'Note 2'})
        
        # Second doc has score below threshold (0.65)
        mock_db.similarity_search_with_score.return_value = [
            (doc1, 0.9),
            (doc2, 0.3)
        ]
        
        results = builder.retrieve_with_mmr("test query", k=5)
        
        # Only doc1 should pass threshold
        assert len(results) == 1
        assert doc1 in results
        assert doc2 not in results
    
    def test_retrieve_with_mmr_empty_results(self, builder, mock_db):
        """Test MMR handles empty results"""
        mock_db.similarity_search_with_score.return_value = []
        
        results = builder.retrieve_with_mmr("test query", k=5)
        
        assert results == []
    
    def test_retrieve_with_mmr_fallback(self, builder, mock_db):
        """Test fallback when MMR not available"""
        # Simulate AttributeError (similarity_search_with_score not available)
        mock_db.similarity_search_with_score.side_effect = AttributeError()
        mock_db.similarity_search.return_value = [Document(page_content="fallback doc")]
        
        results = builder.retrieve_with_mmr("test query", k=5)
        
        assert len(results) == 1
        mock_db.similarity_search.assert_called_once_with("test query", k=5)
    
    def test_get_project_context_success(self, builder, tmp_path, monkeypatch):
        """Test loading project context successfully"""
        # Create temp project directory
        project_dir = tmp_path / "projects" / "test_project"
        project_dir.mkdir(parents=True)
        
        # Create active_record.md
        active_record = project_dir / "active_record.md"
        active_record.write_text("# Test Project\nSome content")
        
        # Mock config.PROJECTS_DIR
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(tmp_path / "projects"))
        
        context = builder.get_project_context("test_project")
        
        assert "# Test Project" in context
        assert "Some content" in context
    
    def test_get_project_context_missing_file(self, builder, tmp_path, monkeypatch):
        """Test handling missing active_record.md"""
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(tmp_path / "projects"))
        
        context = builder.get_project_context("nonexistent_project")
        
        assert context == ""
    
    def test_get_project_context_error_handling(self, builder, monkeypatch):
        """Test error handling in get_project_context"""
        # Mock config to cause OSError
        monkeypatch.setattr('core.config.PROJECTS_DIR', "/invalid/path")
        
        context = builder.get_project_context("test_project")
        
        assert context == ""
    
    def test_build_context_general_mode(self, builder, mock_db):
        """Test building context in GENERAL mode (no project)"""
        doc = Document(page_content="test knowledge", metadata={'title': 'Test Note'})
        mock_db.similarity_search_with_score.return_value = [(doc, 0.9)]
        
        context = builder.build_context("test query", mode="GENERAL")
        
        assert "[NOTE: Test Note]: test knowledge" in context
        assert "[CURRENT ENGAGEMENT LOG]" not in context
    
    def test_build_context_project_mode(self, builder, mock_db, tmp_path, monkeypatch):
        """Test building context in PROJECT mode with active record"""
        # Mock RAG results
        doc = Document(page_content="rag content", metadata={'title': 'RAG Note'})
        mock_db.similarity_search_with_score.return_value = [(doc, 0.9)]
        
        # Create project with active record
        project_dir = tmp_path / "projects" / "test_project"
        project_dir.mkdir(parents=True)
        active_record = project_dir / "active_record.md"
        active_record.write_text("Project log content")
        
        monkeypatch.setattr('core.config.PROJECTS_DIR', str(tmp_path / "projects"))
        
        context = builder.build_context("test query", project="test_project", mode="PROJECT")
        
        assert "[NOTE: RAG Note]: rag content" in context
        assert "[CURRENT ENGAGEMENT LOG]" in context
        assert "Project log content" in context
    
    def test_build_context_no_rag_results(self, builder, mock_db):
        """Test building context when RAG returns no results"""
        mock_db.similarity_search_with_score.return_value = []
        
        context = builder.build_context("test query")
        
        assert "[No relevant knowledge found in database]" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
