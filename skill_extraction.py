import re

def extract_skills(skills, JD):
    skills_extracted = []
    description  =JD.lower()
    for skill in skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, description):
            skills_extracted.append(skill)
    return skills_extracted
