"""
Tests for Ollama Client module.
Tests model validation, retry logic, and AI classification.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from core.ollama_client import OllamaClient


class TestOllamaClient:
    """Test suite for OllamaClient class"""
    
    @patch('core.ollama_client.ollama.list')
    def test_init_with_valid_models(self, mock_list):
        """Test initialization with valid models"""
        mock_list.return_value = {
            'models': [
                {'name': 'strategist'},
                {'name': 'specialist'}
            ]
        }
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        
        assert client.strategist_model == 'strategist'
        assert client.specialist_model == 'specialist'
    
    @patch('core.ollama_client.ollama.list')
    def test_init_fails_with_missing_models(self, mock_list):
        """Test initialization fails when models are missing"""
        mock_list.return_value = {
            'models': [
                {'name': 'other_model'}
            ]
        }
        
        with pytest.raises(RuntimeError):
            OllamaClient(strategist_model='strategist', specialist_model='specialist')
    
    @patch('core.ollama_client.ollama.list')
    def test_validate_models_success(self, mock_list):
        """Test model validation with available models"""
        mock_list.return_value = {
            'models': [
                {'name': 'strategist'},
                {'name': 'specialist'}
            ]
        }
        
        client = OllamaClient.__new__(OllamaClient)
        client.strategist_model = 'strategist'
        client.specialist_model = 'specialist'
        
        assert client.validate_models() is True
    
    @patch('core.ollama_client.ollama.list')
    def test_validate_models_handles_string_format(self, mock_list):
        """Test model validation handles string list format"""
        mock_list.return_value = ['strategist', 'specialist', 'other']
        
        client = OllamaClient.__new__(OllamaClient)
        client.strategist_model = 'strategist'
        client.specialist_model = 'specialist'
        
        assert client.validate_models() is True
    
    @patch('core.ollama_client.ollama.list')
    def test_validate_models_missing(self, mock_list):
        """Test model validation with missing models"""
        mock_list.return_value = {
            'models': [
                {'name': 'other_model'}
            ]
        }
        
        client = OllamaClient.__new__(OllamaClient)
        client.strategist_model = 'strategist'
        client.specialist_model = 'specialist'
        
        assert client.validate_models() is False
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_call_with_retry_success(self, mock_chat, mock_list):
        """Test successful API call on first attempt"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}]}
        mock_chat.return_value = {'message': {'content': 'Test response'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        response = client.call_with_retry('strategist', [{'role': 'user', 'content': 'test'}])
        
        assert response == 'Test response'
        assert mock_chat.call_count == 1
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    @patch('core.ollama_client.time.sleep')
    def test_call_with_retry_recovers(self, mock_sleep, mock_chat, mock_list):
        """Test retry logic recovers from transient failures"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}]}
        
        # Fail twice, then succeed
        mock_chat.side_effect = [
            Exception("Connection error"),
            Exception("Connection error"),
            {'message': {'content': 'Success'}}
        ]
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        response = client.call_with_retry('strategist', [{'role': 'user', 'content': 'test'}])
        
        assert response == 'Success'
        assert mock_chat.call_count == 3
        assert mock_sleep.call_count == 2
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_call_with_retry_fails_after_max_retries(self, mock_chat, mock_list):
        """Test retry logic fails after max retries"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}]}
        mock_chat.side_effect = Exception("Persistent error")
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        
        with pytest.raises(Exception, match="Persistent error"):
            client.call_with_retry('strategist', [{'role': 'user', 'content': 'test'}], max_retries=3)
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_call_strategist(self, mock_chat, mock_list):
        """Test strategist convenience method"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}]}
        mock_chat.return_value = {'message': {'content': 'Strategic response'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        response = client.call_strategist('What should I do?')
        
        assert response == 'Strategic response'
        mock_chat.assert_called_once()
        assert mock_chat.call_args[1]['model'] == 'strategist'
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_call_specialist(self, mock_chat, mock_list):
        """Test specialist convenience method"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}]}
        mock_chat.return_value = {'message': {'content': 'Tactical response'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        response = client.call_specialist('Give me nmap command')
        
        assert response == 'Tactical response'
        mock_chat.assert_called_once()
        assert mock_chat.call_args[1]['model'] == 'specialist'
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_classify_log_section_enumeration(self, mock_chat, mock_list):
        """Test log classification for enumeration"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}, {'name': 'qwen2:0.5b'}]}
        mock_chat.return_value = {'message': {'content': 'ENUMERATION'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        section = client.classify_log_section('nmap scan', 'Found 3 open ports')
        
        assert section == 'ENUMERATION'
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_classify_log_section_exploitation(self, mock_chat, mock_list):
        """Test log classification for exploitation"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}, {'name': 'qwen2:0.5b'}]}
        mock_chat.return_value = {'message': {'content': 'EXPLOITATION'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        section = client.classify_log_section('exploit MS17-010', 'Shell obtained')
        
        assert section == 'EXPLOITATION'
    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_classify_log_section_post_exploitation(self, mock_chat, mock_list):
        """Test log classification for post-exploitation"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}, {'name': 'qwen2:0.5b'}]}
        # Response contains "POST" to trigger POST-EXPLOITATION classification
        mock_chat.return_value = {'message': {'content': 'POST'}}
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        section = client.classify_log_section('privilege escalation', 'Got SYSTEM access')
        
        assert section == 'POST-EXPLOITATION'

    
    @patch('core.ollama_client.ollama.list')
    @patch('core.ollama_client.ollama.chat')
    def test_classify_log_section_fallback(self, mock_chat, mock_list):
        """Test log classification falls back to ENUMERATION on error"""
        mock_list.return_value = {'models': [{'name': 'strategist'}, {'name': 'specialist'}, {'name': 'qwen2:0.5b'}]}
        mock_chat.side_effect = Exception("Classification error")
        
        client = OllamaClient(strategist_model='strategist', specialist_model='specialist')
        section = client.classify_log_section('test', 'test')
        
        assert section == 'ENUMERATION'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
