"""
Ollama Client Module

Handles all interactions with the Ollama API, including:
- Model validation
- API calls with exponential backoff retry logic
- AI-powered log section classification

This module provides a clean abstraction layer over the Ollama API,
making AI calls more reliable and testable.
"""

import ollama
import time
from typing import List, Dict
from core import config


class OllamaClient:
    """
    Wrapper for Ollama API with retry logic and model validation.
    """
    
    def __init__(self, strategist_model: str = None, specialist_model: str = None):
        """
        Initialize Ollama client with model names.
        
        Args:
            strategist_model: Name of strategic AI model (default: from config)
            specialist_model: Name of tactical AI model (default: from config)
        """
        self.strategist_model = strategist_model or config.STRATEGIST_MODEL
        self.specialist_model = specialist_model or config.SPECIALIST_MODEL
        
        # Validate models on initialization
        if not self.validate_models():
            raise RuntimeError("Ollama model validation failed")
    
    def validate_models(self) -> bool:
        """
        Validates that required Ollama models are available.
        
        Returns:
            True if all models are available, False otherwise
        """
        try:
            available = ollama.list()
            
            # Handle different response formats
            if isinstance(available, dict):
                models = available.get('models', [])
            else:
                models = available
            
            # Extract model names - handle both 'name' and 'model' keys
            model_names = []
            for m in models:
                if isinstance(m, dict):
                    name = m.get('name') or m.get('model', '')
                    if name:
                        model_names.append(name)
                elif isinstance(m, str):
                    model_names.append(m)
            
            if not model_names:
                print("⚠️  WARNING: Could not retrieve model list from Ollama.")
                print("Attempting to proceed anyway...")
                return True  # Allow to proceed if we can't get the list
            
            missing = []
            if self.strategist_model not in model_names:
                missing.append(self.strategist_model)
            if self.specialist_model not in model_names:
                missing.append(self.specialist_model)
            
            if missing:
                print(f"❌ CRITICAL ERROR: Missing Ollama models: {', '.join(missing)}")
                print(f"\nAvailable models: {', '.join(model_names)}")
                print(f"\nPlease ensure the following models are installed:")
                print(f"  - {self.strategist_model}")
                print(f"  - {self.specialist_model}")
                return False
            
            print(f"✅ Models validated: {self.strategist_model}, {self.specialist_model}")
            return True
        except Exception as e:
            print(f"❌ Cannot connect to Ollama service: {e}")
            print("Please ensure Ollama is running.")
            return False
    
    def call_with_retry(self, model: str, messages: List[Dict], max_retries: int = None) -> str:
        """
        Call Ollama API with exponential backoff retry logic.
        
        Args:
            model: Model name to use
            messages: List of message dicts with 'role' and 'content'
            max_retries: Maximum retry attempts (default: from config)
            
        Returns:
            AI response content as string
            
        Raises:
            Exception: If all retries fail
        """
        if max_retries is None:
            max_retries = config.OLLAMA_MAX_RETRIES
        
        for attempt in range(max_retries):
            try:
                response = ollama.chat(model=model, messages=messages)
                return response['message']['content']
            except Exception as e:
                if attempt == max_retries - 1:
                    # Final attempt failed
                    raise
                
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"⚠️  Retry {attempt + 1}/{max_retries} (waiting {wait_time}s): {e}")
                time.sleep(wait_time)
    
    def call_strategist(self, prompt: str) -> str:
        """
        Call the strategist model with a prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            AI response
        """
        return self.call_with_retry(
            self.strategist_model,
            [{'role': 'user', 'content': prompt}]
        )
    
    def call_specialist(self, prompt: str) -> str:
        """
        Call the specialist model with a prompt.
        
        Args:
            prompt: User prompt
            
        Returns:
            AI response
        """
        return self.call_with_retry(
            self.specialist_model,
            [{'role': 'user', 'content': prompt}]
        )
    
    def classify_log_section(self, user_query: str, ai_response: str) -> str:
        """
        Uses AI to classify which pentesting section an action belongs to.
        
        Args:
            user_query: User's query or action
            ai_response: AI's response
            
        Returns:
            Section name: 'ENUMERATION', 'EXPLOITATION', or 'POST-EXPLOITATION'
        """
        try:
            prompt = f"""Classify this pentesting action into ONE category:

ENUMERATION: Scanning, discovery, reconnaissance, information gathering
EXPLOITATION: Exploiting vulnerabilities, gaining initial access
POST-EXPLOITATION: Privilege escalation, lateral movement, persistence

User: "{user_query[:200]}"
AI: "{ai_response[:200]}"

Answer with ONE WORD:"""
            
            # Use fast model for classification
            result = self.call_with_retry(
                config.LOG_CLASSIFIER_MODEL,
                [{'role': 'user', 'content': prompt}],
                max_retries=1
            )
            
            result_upper = result.upper()
            if "ENUMERATION" in result_upper:
                return "ENUMERATION"
            elif "EXPLOITATION" in result_upper:
                return "EXPLOITATION"
            elif "POST" in result_upper:
                return "POST-EXPLOITATION"
            else:
                return "ENUMERATION"  # Default fallback
        except Exception as e:
            print(f"⚠️  Log classification failed: {e}")
            return "ENUMERATION"  # Safe default
