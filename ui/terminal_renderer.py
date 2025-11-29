import re

class TerminalRenderer:
    """
    Renders Markdown text with ANSI color codes for terminal display.
    Supports headers, bold, italic, code blocks, inline code, lists, and links.
    """
    
    # ANSI Color Codes
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright Colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background Colors
    BG_BLACK = "\033[40m"
    BG_GRAY = "\033[100m"
    BG_BLUE = "\033[44m"
    
    def __init__(self, enabled=True):
        """Initialize the renderer with optional enable/disable"""
        self.enabled = enabled
    
    def render(self, text):
        """Main rendering function that processes markdown text"""
        if not self.enabled:
            return text
        
        # Process in order to avoid conflicts
        lines = text.split('\n')
        rendered_lines = []
        in_code_block = False
        code_lang = None
        code_lines = []
        
        for line in lines:
            # Check for code block markers (allow leading whitespace for indented blocks)
            code_block_match = re.match(r'^\s*```(\w*)$', line)
            if code_block_match:
                if in_code_block:
                    # End of code block
                    rendered_lines.append(self._render_code_block(code_lines, code_lang))
                    code_lines = []
                    in_code_block = False
                    code_lang = None
                else:
                    # Start of code block
                    in_code_block = True
                    code_lang = code_block_match.group(1) or 'text'
                continue
            
            if in_code_block:
                code_lines.append(line)
                continue
            
            # Process regular line
            rendered_line = self._render_line(line)
            rendered_lines.append(rendered_line)
        
        return '\n'.join(rendered_lines)
    
    def _render_line(self, line):
        """Render a single line of markdown"""
        # Headers (must be checked before other inline elements)
        if line.startswith('# '):
            return f"{self.BOLD}{self.BRIGHT_CYAN}{line[2:]}{self.RESET}"
        elif line.startswith('## '):
            return f"{self.BOLD}{self.CYAN}{line[3:]}{self.RESET}"
        elif line.startswith('### '):
            return f"{self.BOLD}{self.BLUE}{line[4:]}{self.RESET}"
        elif line.startswith('#### '):
            return f"{self.BRIGHT_BLUE}{line[5:]}{self.RESET}"
        
        # Lists
        if re.match(r'^\s*[-*+]\s', line):
            # Bullet list
            indent = len(line) - len(line.lstrip())
            content = re.sub(r'^(\s*)[-*+]\s', '', line)
            bullet = f"{self.BRIGHT_YELLOW}•{self.RESET}"
            return f"{' ' * indent}{bullet} {self._render_inline(content)}"
        
        if re.match(r'^\s*\d+\.\s', line):
            # Numbered list
            match = re.match(r'^(\s*)(\d+\.)\s(.*)$', line)
            if match:
                indent, number, content = match.groups()
                number_styled = f"{self.BRIGHT_YELLOW}{number}{self.RESET}"
                return f"{indent}{number_styled} {self._render_inline(content)}"
        
        # Regular line with inline formatting
        return self._render_inline(line)
    
    def _render_inline(self, text):
        """Render inline markdown elements like bold, italic, code, links"""
        # Inline code (must be done before bold/italic to avoid conflicts)
        text = re.sub(
            r'`([^`]+)`',
            lambda m: f"{self.BG_GRAY}{self.YELLOW}{m.group(1)}{self.RESET}",
            text
        )
        
        # Bold
        text = re.sub(
            r'\*\*([^*]+)\*\*',
            lambda m: f"{self.BOLD}{self.BRIGHT_WHITE}{m.group(1)}{self.RESET}",
            text
        )
        
        # Italic
        text = re.sub(
            r'\*([^*]+)\*',
            lambda m: f"{self.DIM}{m.group(1)}{self.RESET}",
            text
        )
        
        # Links [text](url)
        text = re.sub(
            r'\[([^\]]+)\]\(([^)]+)\)',
            lambda m: f"{self.UNDERLINE}{self.CYAN}{m.group(1)}{self.RESET} {self.DIM}({m.group(2)}){self.RESET}",
            text
        )
        
        return text
    
    def _render_code_block(self, lines, lang):
        """Render a code block with optional syntax highlighting"""
        if not lines:
            return ""
        
        # Language label with separator
        result = []
        if lang:
            lang_label = f"{self.BG_GRAY}{self.BRIGHT_CYAN}┌─ {lang.upper()} {self.RESET}"
            result.append(lang_label)
        
        # Render code lines with syntax highlighting (no border bars)
        for line in lines:
            styled_line = self._syntax_highlight(line, lang)
            result.append(styled_line)
        
        # Bottom separator
        if lang:
            result.append(f"{self.BG_GRAY}{self.BRIGHT_BLACK}└{'─' * 40}{self.RESET}")
        
        return '\n'.join(result)
    
    def _syntax_highlight(self, line, lang):
        """Apply basic syntax highlighting based on language"""
        if not lang or lang == 'text':
            return f"{self.WHITE}{line}{self.RESET}"
        
        # Python syntax highlighting
        if lang in ['python', 'py']:
            # Keywords
            line = re.sub(
                r'\b(def|class|import|from|if|else|elif|for|while|return|try|except|with|as|pass|break|continue|lambda|yield)\b',
                lambda m: f"{self.MAGENTA}{m.group(1)}{self.RESET}",
                line
            )
            # Strings
            line = re.sub(
                r'(["\'])([^\1]*?)\1',
                lambda m: f"{self.GREEN}{m.group(0)}{self.RESET}",
                line
            )
            # Comments
            line = re.sub(
                r'(#.*)$',
                lambda m: f"{self.BRIGHT_BLACK}{m.group(1)}{self.RESET}",
                line
            )
            # Functions
            line = re.sub(
                r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(',
                lambda m: f"{self.BRIGHT_BLUE}{m.group(1)}{self.RESET}(",
                line
            )
        
        # Bash/Shell syntax highlighting
        elif lang in ['bash', 'sh', 'shell']:
            # Commands
            line = re.sub(
                r'\b(cat|grep|ls|cd|pwd|echo|export|sudo|chmod|chown|find|sed|awk|curl|wget)\b',
                lambda m: f"{self.BRIGHT_MAGENTA}{m.group(1)}{self.RESET}",
                line
            )
            # Strings
            line = re.sub(
                r'(["\'])([^\1]*?)\1',
                lambda m: f"{self.GREEN}{m.group(0)}{self.RESET}",
                line
            )
            # Comments
            line = re.sub(
                r'(#.*)$',
                lambda m: f"{self.BRIGHT_BLACK}{m.group(1)}{self.RESET}",
                line
            )
            # Variables
            line = re.sub(
                r'\$\{?([a-zA-Z_][a-zA-Z0-9_]*)\}?',
                lambda m: f"{self.YELLOW}{m.group(0)}{self.RESET}",
                line
            )
        
        # Default: just make it white
        else:
            return f"{self.WHITE}{line}{self.RESET}"
        
        return line


# Convenience function for quick rendering
def render_markdown(text, enabled=True):
    """Quick function to render markdown text"""
    renderer = TerminalRenderer(enabled=enabled)
    return renderer.render(text)

