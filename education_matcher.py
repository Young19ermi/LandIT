import re


# Degree fields we want to recognize
degree_fields = [
    "computer science",
    "software engineering",
    "computer engineering",
    "information technology",
    "information systems",
    "data science",
    "mathematics",
    "statistics",
    "electrical engineering",
    "mechanical engineering",
    "civil engineering",
    "environmental engineering"
]


def extract_education_section(resume):
    """
    Extract only the Education section from a resume.

    Returns:
        str: Education section.
             Returns an empty string if no section is found.
    """

    education_pattern = (
        r'\b(?:education|academic\s+background|'
        r'educational\s+background)\b'
    )

    next_section_pattern = (
        r'\b(?:experience|work\s+experience|'
        r'professional\s+experience|projects|'
        r'skills|certifications|awards|'
        r'languages|references)\b'
    )

    match = re.search(
        education_pattern,
        resume,
        re.IGNORECASE
    )

    if not match:
        return ""

    education_start = match.end()

    remaining_text = resume[education_start:]

    next_section = re.search(
        next_section_pattern,
        remaining_text,
        re.IGNORECASE
    )

    if next_section:
        return remaining_text[:next_section.start()]

    return remaining_text


def extract_required_degrees(
    job_description,
    degree_fields
):
    description = job_description.lower()

    required_degrees = []

    for degree in degree_fields:
        if degree in description:
            required_degrees.append(degree)

    return required_degrees


def extract_candidate_degrees(
    education_section,
    degree_fields
):
    if not education_section:
        return []
    education = education_section.lower()

    candidate_degrees = []

    for degree in degree_fields:
        if degree in education:
            candidate_degrees.append(degree)

    return candidate_degrees

def education_matcher(resume_text, JD):
    education_section = extract_education_section(resume_text)
    required_degrees = extract_required_degrees(JD, degree_fields)

    candidate_degrees = extract_candidate_degrees(education_section, degree_fields)

    # Calculate the education match Score
    if not required_degrees:
        return 100
    if  not candidate_degrees:
        return 0

    matched_degrees = len(set(candidate_degrees).intersection(set(required_degrees))) 
    score = (matched_degrees / len(required_degrees)) * 100
    score = min(score, 100)
    return score