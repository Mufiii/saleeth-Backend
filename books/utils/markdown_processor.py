"""
Markdown processing utility for converting markdown to HTML and extracting TOC.
"""
import markdown
from bs4 import BeautifulSoup
import re
from typing import Dict, List
from django.utils.text import slugify


def process_markdown(markdown_text: str) -> Dict[str, any]:
    """
    Convert markdown to HTML and extract TOC from headings.
    
    Args:
        markdown_text: Markdown content string
        
    Returns:
        Dictionary with 'html' (string) and 'toc' (list) keys.
        If markdown_text is empty, returns {'html': '', 'toc': []}
    """
    if not markdown_text or not markdown_text.strip():
        return {'html': '', 'toc': []}
    
    # Configure markdown extensions
    extensions = [
        'markdown.extensions.toc',
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
    ]
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=extensions)
    html = md.convert(markdown_text)
    
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Extract headings (h1-h4)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
    
    # Generate TOC array and ensure unique IDs
    toc = []
    used_ids = set()
    id_counter = {}
    
    for heading in headings:
        # Get heading text
        title = heading.get_text().strip()
        if not title:
            continue
        
        # Get heading level (1-4)
        level = int(heading.name[1])
        
        # Generate slug-based ID
        base_id = slugify(title)
        if not base_id:
            # Fallback if slugify returns empty
            base_id = f"heading-{len(toc)}"
        
        # Ensure unique ID
        heading_id = base_id
        if heading_id in used_ids:
            counter = id_counter.get(heading_id, 0) + 1
            id_counter[heading_id] = counter
            heading_id = f"{base_id}-{counter}"
        
        used_ids.add(heading_id)
        
        # Set ID attribute on heading element
        heading['id'] = heading_id
        
        # Add to TOC
        toc.append({
            'id': heading_id,
            'title': title,
            'level': level
        })
    
    # Return processed HTML and TOC
    return {
        'html': str(soup),
        'toc': toc
    }

