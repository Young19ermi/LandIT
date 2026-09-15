import re


def extract_responsibilities(job_description):

    responsibilities_pattern = (
        r'\b(?:responsibilities|'
        r'key\s+responsibilities|'
        r'what\s+you(?:\'ll| will)\s+do|'
        r'role\s+responsibilities|'
        r'what\s+you(?:\'ll| will)\s+be\s+doing)\b'
    )

    next_section_pattern = (
        r'\b(?:requirements|qualifications|'
        r'required\s+skills|'
        r'preferred\s+qualifications|'
        r'benefits|'
        r'about\s+us|'
        r'education|'
        r'skills)\b'
    )

    match = re.search(
        responsibilities_pattern,
        job_description,
        re.IGNORECASE
    )

    if not match:
        return ""

    responsibilities_start = match.end()

    remaining_text = job_description[
        responsibilities_start:
    ]

    next_section = re.search(
        next_section_pattern,
        remaining_text,
        re.IGNORECASE
    )

    if next_section:
        return remaining_text[:next_section.start()]

    return remaining_text