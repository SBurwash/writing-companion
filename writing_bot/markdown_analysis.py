import re
from typing import List, Tuple

def extract_style_and_process(markdown_text: str) -> Tuple[List[str], List[str]]:
    style_elements = set()
    process_steps = set()

    # Style: Headings
    if re.search(r'^#+ ', markdown_text, re.MULTILINE):
        style_elements.add("uses_headings")
    # Style: Bullet lists
    if re.search(r'^\s*[-*+] ', markdown_text, re.MULTILINE):
        style_elements.add("uses_bullet_lists")
    # Style: Bold
    if re.search(r'\*\*[^*]+\*\*', markdown_text):
        style_elements.add("uses_bold")
    # Style: Italic
    if re.search(r'\*[^*]+\*', markdown_text):
        style_elements.add("uses_italic")
    # Style: Average sentence length
    sentences = re.split(r'[.!?]', markdown_text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len < 12:
            style_elements.add("short_sentences")
        elif avg_len > 20:
            style_elements.add("long_sentences")
        else:
            style_elements.add("medium_sentences")

    # Process: Starts with a question
    first_line = markdown_text.strip().split('\n', 1)[0]
    if '?' in first_line:
        process_steps.add("starts_with_question")
    # Process: Has summary section
    if re.search(r'(?i)summary', markdown_text):
        process_steps.add("has_summary_section")
    # Process: Has call to action
    if re.search(r'(?i)call to action|let\'s|contact|subscribe|learn more', markdown_text):
        process_steps.add("has_call_to_action")

    return list(style_elements), list(process_steps) 