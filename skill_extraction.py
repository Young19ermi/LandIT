
import re


# Different names that should be treated as the same skill
skill_aliases = {
    "react.js": "react",
    "reactjs": "react",

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


def extract_skills(skills, content):
    skills_extracted = []
    description = content.lower()

    for skill in skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, description):
            # Convert the detected skill to its standard name
            normalized_skill = skill_aliases.get(
                skill.lower(),
                skill.lower()
            )

            skills_extracted.append(normalized_skill)

    return skills_extracted


# List of canonical skills
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


# Extract skills from resume and job description
"""Here for Resue and JD,I can use the input directly here"""
result_resume = extract_skills(skills, resume)
result_job_description = extract_skills(skills, job_description)


def similarity_score(resume_skills, job_skills):
    if not resume_skills or not job_skills:
        return 0

    resume_skills = set(resume_skills)
    job_skills = set(job_skills)

    # Skills that appear in both the resume and JD
    intersection = resume_skills.intersection(job_skills)

    # Percentage of JD skills that the resume has
    return (len(intersection) / len(job_skills)) * 100


# Calculate the skill match percentage
score = similarity_score(
    result_resume,
    result_job_description
)

