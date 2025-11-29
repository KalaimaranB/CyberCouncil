"""
Context Builder Module

Handles context retrieval and assembly for AI queries:
- RAG (Retrieval-Augmented Generation) with MMR (Max Marginal Relevance)
- Project-specific active record context
- Quality filtering and diversity optimization

This module provides intelligent context assembly that balances relevance
and diversity, ensuring the AI has the best information without redundancy.
"""

import os
from typing import List, Optional
from langchain_core.documents import Document
from langchain_chroma import Chroma
from core import config


class ContextBuilder:
    """
    Builds intelligent context for AI queries using RAG and project logs.
    """
    
    def __init__(self, db: Chroma):
        """
        Initialize context builder with vector database.
        
        Args:
            db: ChromaDB vector database instance
        """
        self.db = db
    
    def retrieve_with_mmr(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieves documents using Maximal Marginal Relevance for diversity.
        Balances relevance with diversity to avoid redundant results.
        
        Args:
            query: Search query
            k: Number of documents to retrieve (default: 5)
            
        Returns:
            List of Document objects, ranked by MMR score
        """
        try:
            # Get more candidates than needed
            candidates = self.db.similarity_search_with_score(query, k=config.RAG_CANDIDATE_K)
            
            # Filter by relevance threshold
            relevant = [(doc, score) for doc, score in candidates if score >= config.RAG_RELEVANCE_THRESHOLD]
            
            if not relevant:
                return []
            
            # MMR selection
            selected = []
            remaining = relevant.copy()
            
            # Always select most relevant first
            if remaining:
                best_doc, best_score = max(remaining, key=lambda x: x[1])
                selected.append(best_doc)
                remaining.remove((best_doc, best_score))
            
            # Select remaining docs balancing relevance and diversity
            while len(selected) < k and remaining:
                best_score_val = -999
                best_item = None
                
                for doc, relevance in remaining:
                    # Calculate similarity to already selected docs
                    if selected:
                        # Simple diversity check: avoid docs with too similar content
                        max_similarity = max(
                            len(set(doc.page_content.split()) & set(s.page_content.split())) / 
                            max(len(doc.page_content.split()), len(s.page_content.split()))
                            for s in selected
                        )
                    else:
                        max_similarity = 0
                    
                    # MMR score: balance relevance vs diversity
                    mmr_score = (config.MMR_LAMBDA * relevance) - ((1 - config.MMR_LAMBDA) * max_similarity)
                    
                    if mmr_score > best_score_val:
                        best_score_val = mmr_score
                        best_item = (doc, relevance)
                
                if best_item:
                    selected.append(best_item[0])
                    remaining.remove(best_item)
                else:
                    break
            
            return selected
            
        except AttributeError:
            # Fallback if similarity_search_with_score not available
            print("⚠️  Using fallback retrieval (MMR not available)")
            return self.db.similarity_search(query, k=k)
    
    def get_project_context(self, project_name: str) -> str:
        """
        Load project-specific context from active_record.md.
        
        Args:
            project_name: Name of the project
            
        Returns:
            Project context as string, empty if not found or error
        """
        try:
            path = f"{config.PROJECTS_DIR}/{project_name}/active_record.md"
            
            if not os.path.exists(path):
                return ""
            
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"⚠️  Warning: Could not load project context: {e}")
            return ""
    
    def build_context(self, query: str, project: Optional[str] = None, mode: str = "GENERAL") -> str:
        """
        Build complete context combining RAG and project logs.
        
        Args:
            query: User query for RAG retrieval
            project: Project name (optional)
            mode: Context mode - "PROJECT" or "GENERAL"
            
        Returns:
            Complete context string
        """
        # 1. Get RAG results with MMR for quality and diversity
        docs = self.retrieve_with_mmr(query, k=config.RAG_RETRIEVAL_K)
        
        if docs:
            rag_text = "\n".join([f"[NOTE: {d.metadata.get('title', 'General')}]: {d.page_content}" for d in docs])
        else:
            rag_text = "[No relevant knowledge found in database]"
        
        # 2. Get Project Context (Active Record)
        project_text = ""
        if project and mode == "PROJECT":
            project_content = self.get_project_context(project)
            if project_content:
                project_text = f"\n[CURRENT ENGAGEMENT LOG]:\n{project_content}"
        
        return f"{rag_text}\n{project_text}"
