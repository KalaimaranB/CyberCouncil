"""
Tests for Terminal Renderer module.
Tests markdown rendering, syntax highlighting, and edge cases.
"""

import pytest
from ui.terminal_renderer import TerminalRenderer, render_markdown


class TestTerminalRenderer:
    """Test suite for TerminalRenderer class"""
    
    def test_init(self):
        """Test renderer initialization"""
        renderer = TerminalRenderer(enabled=True)
        assert renderer.enabled is True
        
        renderer_disabled = TerminalRenderer(enabled=False)
        assert renderer_disabled.enabled is False
    
    def test_render_disabled(self):
        """Test that rendering can be disabled"""
        renderer = TerminalRenderer(enabled=False)
        text = "# Header\n**Bold** and *italic*"
        
        result = renderer.render(text)
        assert result == text  # Should return unchanged
    
    def test_render_headers(self):
        """Test header rendering"""
        renderer = TerminalRenderer()
        
        # Test H1
        result = renderer.render("# Main Header")
        assert "Main Header" in result
        assert renderer.BRIGHT_CYAN in result
        
        # Test H2
        result = renderer.render("## Sub Header")
        assert "Sub Header" in result
        assert renderer.CYAN in result
        
        # Test H3
        result = renderer.render("### Third Header")
        assert "Third Header" in result
        assert renderer.BLUE in result
        
        # Test H4
        result = renderer.render("#### Fourth Header")
        assert "Fourth Header" in result
        assert renderer.BRIGHT_BLUE in result
    
    def test_render_bold(self):
        """Test bold text rendering"""
        renderer = TerminalRenderer()
        
        result = renderer.render("This is **bold text** here")
        assert "bold text" in result
        assert renderer.BOLD in result
    
    def test_render_italic(self):
        """Test italic text rendering"""
        renderer = TerminalRenderer()
        
        result = renderer.render("This is *italic text* here")
        assert "italic text" in result
        assert renderer.DIM in result
    
    def test_render_inline_code(self):
        """Test inline code rendering"""
        renderer = TerminalRenderer()
        
        result = renderer.render("Here is `inline code` in text")
        assert "inline code" in result
        assert renderer.BG_GRAY in result
        assert renderer.YELLOW in result
    
    def test_render_code_block_python(self):
        """Test Python code block rendering"""
        renderer = TerminalRenderer()
        
        code = """```python
def hello():
    print("Hello")
    return True
```"""
        
        result = renderer.render(code)
        assert "PYTHON" in result
        assert "hello" in result  # Function name should be present
        assert "print" in result
        assert "return" in result
    
    def test_render_code_block_bash(self):
        """Test Bash code block rendering"""
        renderer = TerminalRenderer()
        
        code = """```bash
echo "test"
grep -r pattern /var/log/
export VAR="value"
```"""
        
        result = renderer.render(code)
        assert "BASH" in result
        assert "echo" in result
        assert "grep" in result
        assert "export" in result
    
    def test_render_code_block_no_language(self):
        """Test code block without language specification"""
        renderer = TerminalRenderer()
        
        code = """```
plain text code
no highlighting
```"""
        
        result = renderer.render(code)
        assert "plain text code" in result
        assert "no highlighting" in result
    
    def test_render_indented_code_block(self):
        """Test indented code blocks (common in lists)"""
        renderer = TerminalRenderer()
        
        code = """1. First step:
   ```bash
   nmap -sV target
   ```"""
        
        result = renderer.render(code)
        assert "BASH" in result
        assert "nmap" in result
    
    def test_render_bullet_list(self):
        """Test bullet list rendering"""
        renderer = TerminalRenderer()
        
        text = """- First item
- Second item
- Third item"""
        
        result = renderer.render(text)
        assert "First item" in result
        assert "Second item" in result
        assert renderer.BRIGHT_YELLOW in result  # Bullet color
    
    def test_render_numbered_list(self):
        """Test numbered list rendering"""
        renderer = TerminalRenderer()
        
        text = """1. First
2. Second
3. Third"""
        
        result = renderer.render(text)
        assert "First" in result
        assert "Second" in result
        assert renderer.BRIGHT_YELLOW in result  # Number color
    
    def test_render_nested_list(self):
        """Test nested list rendering"""
        renderer = TerminalRenderer()
        
        text = """- Parent item
  - Nested item
  - Another nested"""
        
        result = renderer.render(text)
        assert "Parent item" in result
        assert "Nested item" in result
    
    def test_render_link(self):
        """Test link rendering"""
        renderer = TerminalRenderer()
        
        text = "[Click here](https://example.com)"
        result = renderer.render(text)
        
        assert "Click here" in result
        assert "https://example.com" in result
        assert renderer.CYAN in result
    
    def test_render_mixed_formatting(self):
        """Test multiple formatting elements in one line"""
        renderer = TerminalRenderer()
        
        text = "This has **bold** and *italic* and `code`"
        result = renderer.render(text)
        
        assert "bold" in result
        assert "italic" in result
        assert "code" in result
    
    def test_empty_code_block(self):
        """Test empty code block handling"""
        renderer = TerminalRenderer()
        
        code = """```
```"""
        
        result = renderer.render(code)
        # Should not crash
        assert result is not None
    
    def test_malformed_markdown(self):
        """Test handling of malformed markdown"""
        renderer = TerminalRenderer()
        
        # Unclosed bold
        result = renderer.render("This is **unclosed bold")
        assert result is not None
        
        # Unclosed code
        result = renderer.render("This is `unclosed code")
        assert result is not None
        
        # Empty string
        result = renderer.render("")
        assert result == ""
    
    def test_multiline_text(self):
        """Test rendering multiline text"""
        renderer = TerminalRenderer()
        
        text = """# Header
First paragraph

Second paragraph"""
        
        result = renderer.render(text)
        assert "Header" in result
        assert "First paragraph" in result
        assert "Second paragraph" in result
    
    def test_render_markdown_convenience_function(self):
        """Test the convenience function"""
        text = "# Header\n**Bold**"
        
        result = render_markdown(text, enabled=True)
        assert "Header" in result
        assert "Bold" in result
        
        result_disabled = render_markdown(text, enabled=False)
        assert result_disabled == text
    
    def test_code_block_preserves_content(self):
        """Test that code blocks preserve exact content"""
        renderer = TerminalRenderer()
        
        code = """```python
x = 10
if x > 5:
    print("Greater")
```"""
        
        result = renderer.render(code)
        assert "x = 10" in result
        assert "x > 5:" in result  # Check for expression, not full line
        assert "Greater" in result  # Check for string content
    
    def test_python_syntax_highlighting(self):
        """Test Python-specific syntax highlighting"""
        renderer = TerminalRenderer()
        
        # Test keyword highlighting
        line = renderer._syntax_highlight("def my_function():", "python")
        assert "def" in line
        assert "my_function" in line
        
        # Test comment highlighting
        line = renderer._syntax_highlight("# This is a comment", "python")
        assert "This is a comment" in line
    
    def test_bash_syntax_highlighting(self):
        """Test Bash-specific syntax highlighting"""
        renderer = TerminalRenderer()
        
        # Test command highlighting
        line = renderer._syntax_highlight("echo 'hello'", "bash")
        assert "echo" in line
        assert "hello" in line
        
        # Test variable highlighting
        line = renderer._syntax_highlight("export VAR=value", "bash")
        assert "export" in line
        assert "VAR" in line
    
    def test_ansi_reset_codes(self):
        """Test that ANSI reset codes are present"""
        renderer = TerminalRenderer()
        
        result = renderer.render("**Bold**")
        # Should have reset codes to prevent color bleeding
        assert renderer.RESET in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
