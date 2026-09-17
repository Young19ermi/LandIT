import re


# Different names that should be treated as the same skill.
skill_aliases = {
    "react.js": "react",
    "reactjs": "react",
    "css3": "css",
    "html5": "html",

    "node": "node.js",
    "nodejs": "node.js",

    "next": "next.js",
    "nextjs": "next.js",

    "js": "javascript",
    "ts": "typescript",

    "postgres": "postgresql",

    "vue.js": "vue",
    "vuejs": "vue",

    "express.js": "express",

    "sklearn": "scikit-learn",
    "scikit learn": "scikit-learn",

    "tailwindcss": "tailwind",
}


# List of canonical skills.
skills = [
    # languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "sql", "html", "css",
    "html5", "css3",

    # frontend
    "react", "vue", "angular", "next.js", "nuxt", "svelte", "redux", "mobx",
    "tailwind", "bootstrap", "material-ui", "webpack", "vite", "sass",
    "d3.js", "three.js",

    # backend
    "node.js", "express", "django", "flask", "fastapi", "spring", "spring boot",
    "rails", ".net", "graphql", "rest api", "grpc", "microservices", "kafka",
    "rabbitmq", "nginx", "oauth", "jwt", "websockets",

    # data / ml
    "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "keras",
    "machine learning", "deep learning", "nlp", "computer vision", "opencv",
    "data pipeline", "etl", "spark", "hadoop", "hive", "airflow",
    "snowflake", "bigquery", "redshift", "tableau", "power bi", "looker",

    # cloud / infra
    "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "ansible",
    "ci/cd", "jenkins", "github actions", "gitlab ci", "linux", "unix",

    # databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "dynamodb",
    "sqlite", "cassandra",

    # mobile / other platforms
    "android", "ios", "flutter", "react native", "unity", "unreal engine",

    # testing
    "selenium", "cypress", "jest", "pytest", "junit", "mocha", "unit testing",
    "tdd",

    # practices / tools
    "agile", "scrum", "system design", "oop", "design patterns", "api design",
    "code review", "git", "github", "gitlab", "jira", "figma", "bash",

    # business tools
    "excel", "salesforce", "sap", "blockchain", "web3",
]


def extract_skills(skills, content):
    """
    Extract and normalize skills from text.
    """

    if not content:
        return []

    description = content.lower()

    skills_extracted = []

    # Create searchable names:
    # canonical skill names + aliases.
    searchable_skills = list(skills)

    for alias in skill_aliases:
        if alias not in searchable_skills:
            searchable_skills.append(alias)

    for skill in searchable_skills:

        pattern = r'(?<!\w)' + re.escape(
            skill.lower()
        ) + r'(?!\w)'

        if re.search(pattern, description):

            normalized_skill = skill_aliases.get(
                skill.lower(),
                skill.lower()
            )

            if normalized_skill not in skills_extracted:
                skills_extracted.append(
                    normalized_skill
                )

    return skills_extracted

def extract_skills_from_plain_description(job_description):
    if not job_description:
        return
    matched = []
    for words in job_description.split():
        if words.lower() in skills:
            matched.append(words.lower())
    return matched 
def extract_required_skills(job_description):
    """
    Extract skills from the required portion
    of the job description.
    """

    if not job_description:
        return []

    required_pattern = (
        r'\b(?:requirements|'
        r'required\s+skills|'
        r'required\s+qualifications|'
        r'must\s+have|'
        r'what\s+you\s+need)\b'
        r'using re.IGNORECASE'
    )

    next_section_pattern = (
        r'\b(?:preferred\s+qualifications|'
        r'preferred\s+skills|'
        r'nice\s+to\s+have|'
        r'bonus|'
        r'benefits|'
        r'about\s+us|'
        r'responsibilities)\b'
    )

    match = re.search(
        required_pattern,
        job_description,
        re.IGNORECASE
    )

    if not match:
        return []

    required_start = match.end()

    remaining_text = job_description[
        required_start:
    ]

    next_section = re.search(
        next_section_pattern,
        remaining_text,
        re.IGNORECASE
    )

    if next_section:
        required_text = remaining_text[
            :next_section.start()
        ]
    else:
        required_text = remaining_text

    return extract_skills(
        skills,
        required_text
    )


def extract_preferred_skills(job_description):
    """
    Extract skills from the preferred portion
    of the job description.
    """

    if not job_description:
        return []

    preferred_pattern = (
        r'\b(?:preferred\s+qualifications|'
        r'preferred\s+skills|'
        r'nice\s+to\s+have|'
        r'bonus)\b'
    )

    next_section_pattern = (
        r'\b(?:benefits|'
        r'about\s+us|'
        r'responsibilities|'
        r'requirements|'
        r'required\s+skills|'
        r'education)\b'
    )

    match = re.search(
        preferred_pattern,
        job_description,
        re.IGNORECASE
    )

    if not match:
        return []

    preferred_start = match.end()

    remaining_text = job_description[
        preferred_start:
    ]

    next_section = re.search(
        next_section_pattern,
        remaining_text,
        re.IGNORECASE
    )

    if next_section:
        preferred_text = remaining_text[
            :next_section.start()
        ]
    else:
        preferred_text = remaining_text

    return extract_skills(
        skills,
        preferred_text
    )


def similarity_score(resume_skills, job_skills):
    """
    Calculate the percentage of required job skills
    that are present in the resume.
    """

    if not job_skills:
        return 100

    if not resume_skills:
        return 0

    resume_skills = set(resume_skills)
    job_skills = set(job_skills)

    intersection = resume_skills.intersection(
        job_skills
    )

    return (
        len(intersection) / len(job_skills)
    ) * 100


def skill_matcher(resume_text, job_description):
    """
    Main skill matching function.

    Extracts resume skills, required job skills,
    and preferred job skills.

    The main score is based only on required skills.
    Preferred skills are reported separately.
    """

    resume_skills = extract_skills(
        skills,
        resume_text
    )

    required_skill = extract_required_skills(
        job_description
    ) 
    required_skills_from_description = extract_skills_from_plain_description(job_description)
    required_skills = list(set(required_skill + required_skills_from_description))
    print("Required Skills", required_skills)
    print("Resume Skills", resume_skills)

    preferred_skills = extract_preferred_skills(
        job_description
    )

    score = similarity_score(
        resume_skills,
        required_skills
    )

    matched_skills = list(
        set(resume_skills).intersection(
            set(required_skills)
        )
    )

    missing_skills = list(
        set(required_skills) - set(resume_skills)
    )

    matched_preferred = list(
        set(resume_skills).intersection(
            set(preferred_skills)
        )
    )

    missing_preferred = list(
        set(preferred_skills) - set(resume_skills)
    )

    return {
        "score": score,

        "matched": matched_skills,
        "missing": missing_skills,

        "preferred_matched": matched_preferred,
        "preferred_missing": missing_preferred,

        "resume_skills": resume_skills,
        "required": required_skills,
        "preferred": preferred_skills
    }