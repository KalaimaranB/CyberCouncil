import os
import re
import shutil
import glob
import time
from duckduckgo_search import DDGS
from core import config

def sanitize_project_name(name):
    """
    Ensures project names are filesystem-safe and prevents path traversal attacks.
    """
    # Remove any path components (prevents ../../../etc/passwd attacks)
    name = os.path.basename(name)
    
    # Remove special filesystem characters that could cause issues
    # Windows: < > : " / \ | ? *
    # We also remove backticks and other potentially dangerous chars
    name = re.sub(r'[<>:"/\\|?*`]', '', name)
    
    # Remove leading/trailing whitespace and dots
    name = name.strip().strip('.')
    
    # Limit length to prevent filesystem issues
    name = name[:config.MAX_PROJECT_NAME_LENGTH]
    
    # Ensure we have a valid name after sanitization
    if not name or name.isspace():
        name = f"project_{int(time.time())}"
    
    return name

def backup_active_record(project_name):
    """
    Creates a timestamped backup of the active record before modifications.
    Keeps only the last 5 backups to prevent excessive storage usage.
    """
    filepath = f"{config.PROJECTS_DIR}/{project_name}/active_record.md"
    
    if not os.path.exists(filepath):
        return "No active record to backup."
    
    # Create backups directory
    backup_dir = f"{config.PROJECTS_DIR}/{project_name}/backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create timestamped backup
    timestamp = int(time.time())
    backup_path = f"{backup_dir}/active_record_{timestamp}.md"
    
    try:
        shutil.copy2(filepath, backup_path)
        
        # Keep only last 5 backups
        backups = sorted(glob.glob(f"{backup_dir}/active_record_*.md"))
        for old_backup in backups[:-config.MAX_ACTIVE_RECORD_BACKUPS]:
            os.remove(old_backup)
        
        return f"✅ Backup created: {os.path.basename(backup_path)}"
    except Exception as e:
        return f"⚠️ Backup failed: {e}"

def search_official_docs(query):
    """
    Prioritizes official documentation, then writeups, then general.
    """
    print(f"🔎 [Eyes] Searching for: {query}")
    try:
        ddgs = DDGS()
        
        # 1. Construct "Official" Query
        official_query = f"{query} (site:github.com OR site:readthedocs.io OR site:gitbook.io OR site:.org)"
        results = list(ddgs.text(official_query, max_results=2))
        
        # 2. Fallback: Trustworthy Writeups
        if not results:
            print("   -> No official docs found. Checking Writeups...")
            writeup_query = f"{query} (site:hackthebox.com OR site:tryhackme.com OR site:medium.com)"
            results = list(ddgs.text(writeup_query, max_results=2))
        
        if not results:
             return "No reliable results found."

        formatted = ""
        for r in results:
            formatted += f"SOURCE: {r['title']}\nLINK: {r['href']}\nCONTENT: {r['body']}\n\n"
        return formatted
    except Exception as e:
        return f"Search Error: {e}"

def init_project(project_name):
    """Creates the project folder and the template Active Record"""
    # Sanitize project name to prevent path traversal attacks
    project_name = sanitize_project_name(project_name)
    path = f"{config.PROJECTS_DIR}/{project_name}"
    if not os.path.exists(path):
        os.makedirs(path)
        
    record_path = f"{path}/active_record.md"
    
    # Logic: Create if missing, OR repair if empty/broken
    create_new = False
    if not os.path.exists(record_path):
        create_new = True
    else:
        # Check for corruption (missing tags)
        with open(record_path, 'r') as f:
            content = f.read()
        if "<!-- SECTION: ENUMERATION -->" not in content:
            print(f"⚠️ Detected corrupted record for {project_name}. Repairing...")
            create_new = True

    if create_new:
        with open(record_path, 'w') as f:
            f.write(f"# Active Investigation Record: {project_name}\n\n")
            # These tags match the parser in council.py
            f.write("<!-- SECTION: ENUMERATION -->\n\n")
            f.write("<!-- SECTION: EXPLOITATION -->\n\n")
            f.write("<!-- SECTION: POST-EXPLOITATION -->\n\n")
    
    return f"Project {project_name} initialized."

def update_active_record(project_name, section, content):
    """
    Inserts content under the specific HTML comment tag.
    Section options: ENUMERATION, EXPLOITATION, POST-EXPLOITATION
    """
    # Sanitize project name
    project_name = sanitize_project_name(project_name)
    filepath = f"{config.PROJECTS_DIR}/{project_name}/active_record.md"
    if not os.path.exists(filepath):
        return "Error: Project not found."
    
    with open(filepath, 'r') as f:
        data = f.read()
    
    # Regex to find the tag
    tag = "<!-- SECTION: " + section.upper() + " -->"
    
    if tag not in data:
        return f"Error: Section {section} tag missing in file."
        
    # Insert content immediately after the tag
    new_data = data.replace(tag, f"{tag}\n- {content}")
    
    with open(filepath, 'w') as f:
        f.write(new_data)
        
    return f"Updated {section} log."

def get_active_record(project_name):
    """Reads the full active record for the Strategist to summarize"""
    # Sanitize project name
    project_name = sanitize_project_name(project_name)
    path = f"{config.PROJECTS_DIR}/{project_name}/active_record.md"
    if os.path.exists(path):
        with open(path, 'r') as f:
            return f.read()
    return "No records found."

def save_lessons_learned(project_name, lessons_text):
    """
    Saves the AI-generated summary to the project folder AND the permanent knowledge base.
    """
    # Sanitize project name
    project_name = sanitize_project_name(project_name)
    
    # 1. Save local project summary
    project_path = f"{config.PROJECTS_DIR}/{project_name}/summary.md"
    with open(project_path, 'w') as f:
        f.write(lessons_text)
        
    # 2. Save to Global Knowledge Base (so ingest.py can learn from it)
    kb_path = f"{config.NOTES_DIR}/learned"
    if not os.path.exists(kb_path):
        os.makedirs(kb_path)
        
    # We prepend the project name so we know where this lesson came from
    kb_file = f"{kb_path}/{project_name}_lessons.md"
    with open(kb_file, 'w') as f:
        f.write(f"# Lessons Learned from {project_name}\n\n{lessons_text}")
        
    return f"✅ Lessons saved to {project_path} and added to Knowledge Base."