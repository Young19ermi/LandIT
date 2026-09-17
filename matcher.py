import re
import json
import argparse
import difflib
from datetime import date
import requests
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- skill taxonomy ----------

SKILLS = [
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

ALIASES = {
    "js": "javascript", "ts": "typescript", "k8s": "kubernetes",
    "postgres": "postgresql", "node": "node.js", "nodejs": "node.js",
    "reactjs": "react", "vuejs": "vue", "golang": "go", "ml": "machine learning",
    "cicd": "ci/cd", "k8": "kubernetes",
}

REQUIRED_MARKERS = ["required", "must have", "must", "minimum", "essential", "need to have"]
PREFERRED_MARKERS = ["preferred", "nice to have", "a plus", "bonus", "ideally", "plus"]
ACTION_VERBS = {
    "led", "built", "designed", "implemented", "optimized", "reduced", "increased",
    "architected", "developed", "launched", "drove", "spearheaded", "created",
    "improved", "automated", "shipped", "delivered", "managed", "scaled",
    "migrated", "refactored", "mentored", "owned", "established", "streamlined",
    "founded", "grew", "accelerated", "engineered", "deployed",
}
SOFT_SKILLS = [
    "communication", "leadership", "teamwork", "collaboration", "problem-solving",
    "problem solving", "adaptability", "ownership", "mentorship", "stakeholder",
    "cross-functional", "initiative", "time management",
]


def _phrase_pattern(skill: str) -> re.Pattern:
    escaped = re.escape(skill).replace(r"\ ", r"[\s\-]?").replace(r"\.", r"\.?")
    return re.compile(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", re.IGNORECASE)


_SKILL_PATTERNS = {skill: _phrase_pattern(skill) for skill in SKILLS}
_ALIAS_PATTERNS = {alias: _phrase_pattern(alias) for alias in ALIASES}


# ---------- core skill detection ----------

def get_skills(text: str) -> dict:
    """Return {canonical_skill: mention_count}, folding aliases into their canonical form."""
    found = {}
    for skill, pattern in _SKILL_PATTERNS.items():
        n = len(pattern.findall(text))
        if n:
            found[skill] = found.get(skill, 0) + n
    for alias, pattern in _ALIAS_PATTERNS.items():
        n = len(pattern.findall(text))
        if n:
            canonical = ALIASES[alias]
            found[canonical] = found.get(canonical, 0) + n
    return found


def _sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"[.!?\n]+", text) if s.strip()]


def skill_weights(jd_text: str, skills_found: dict) -> dict:
    """
    Weight each JD skill by how urgently it's asked for: 3 if it appears in a
    'required/must-have' sentence, 1 if only in a 'preferred/nice-to-have'
    sentence, 2 otherwise. This beats plain frequency — a skill mentioned
    once as 'required' matters more than one mentioned three times in passing.
    """
    weights = {}
    sentences = _sentences(jd_text)
    for skill in skills_found:
        pattern = _SKILL_PATTERNS.get(skill) or next(
            (p for a, p in _ALIAS_PATTERNS.items() if ALIASES[a] == skill), None
        )
        level = 2
        for sent in sentences:
            if pattern and pattern.search(sent):
                low = sent.lower()
                if any(m in low for m in REQUIRED_MARKERS):
                    level = 3
                    break
                if any(m in low for m in PREFERRED_MARKERS):
                    level = min(level, 1)
        weights[skill] = level
    return weights


# ---------- similarity ----------

def similarity(text_a: str, text_b: str) -> float:
    """Bigram TF-IDF cosine similarity — catches phrases, not just lone words."""
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    tfidf = vec.fit_transform([text_a, text_b])
    return float(cosine_similarity(tfidf[0], tfidf[1])[0][0])


# ---------- resume-quality metrics ----------

def verb_score(resume_text: str) -> float:
    """% of bullet-like lines that open with a strong action verb."""
    lines = [l.strip(" -•\t") for l in resume_text.split("\n") if len(l.strip()) > 15]
    if not lines:
        return 0.0
    hits = sum(1 for l in lines if l.split(" ")[0].lower().strip(",.") in ACTION_VERBS)
    return hits / len(lines)


def quant_ratio(resume_text: str) -> float:
    """% of bullet-like lines containing a number — proxy for quantified impact."""
    lines = [l.strip(" -•\t") for l in resume_text.split("\n") if len(l.strip()) > 15]
    if not lines:
        return 0.0
    hits = sum(1 for l in lines if re.search(r"\d", l))
    return hits / len(lines)


def title_match(resume_text: str, jd_text: str) -> float:
    """Fuzzy match between the JD's title line and the resume's likely title lines."""
    jd_first_lines = [l.strip() for l in jd_text.split("\n")[:5] if l.strip()]
    resume_first_lines = [l.strip() for l in resume_text.split("\n")[:8] if l.strip()]
    if not jd_first_lines or not resume_first_lines:
        return 0.0
    best = 0.0
    for jline in jd_first_lines:
        for rline in resume_first_lines:
            ratio = difflib.SequenceMatcher(None, jline.lower(), rline.lower()).ratio()
            best = max(best, ratio)
    return best


def soft_skills(text: str) -> set:
    low = text.lower()
    return {s for s in SOFT_SKILLS if s in low}


def jd_years(text: str) -> float:
    """JDs rarely have dates — just read the explicit 'X+ years' ask."""
    matches = re.findall(r"(\d+)\s*\+?\s*(?:years|yrs)", text, re.IGNORECASE)
    return max((int(m) for m in matches), default=0)


_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}

_DATE_TOKEN = r"(?:\d{1,2}/\d{4}|[A-Za-z]{3,9}\.?\s+\d{4}|\d{4})"
_DATE_RANGE_RE = re.compile(
    rf"({_DATE_TOKEN})\s*(?:-|–|—|to)\s*({_DATE_TOKEN}|present|current|now|ongoing)",
    re.IGNORECASE,
)


EXPERIENCE_HEADERS = {
    "experience", "professional experience", "work experience",
    "employment history", "relevant experience", "career history",
}
OTHER_HEADERS = {
    "education", "skills", "projects", "certifications", "summary",
    "objective", "awards", "publications", "volunteer", "references",
    "technical skills", "languages", "interests", "activities",
    "professional summary", "core competencies",
}


def _clean_header(line: str) -> str:
    """Strip markdown/bullet noise from a line so it can be compared against header names."""
    return re.sub(r"^[#\-\*\s]+", "", line).strip(" :").lower()


def experience_section(text: str) -> str:
    """
    Slice out just the block under an 'Experience' / 'Professional Experience'
    heading, stopping at the next section heading (Education, Skills, etc.).
    Date ranges are only ever read from inside this slice, so a degree's
    '2016 - 2020' never gets mistaken for work history.
    """
    lines = text.split("\n")
    start = None
    for i, line in enumerate(lines):
        if _clean_header(line) in EXPERIENCE_HEADERS:
            start = i + 1
            break
    if start is None:
        return ""

    collected = []
    for line in lines[start:]:
        if _clean_header(line) in OTHER_HEADERS:
            break
        collected.append(line)
    return "\n".join(collected)


def _to_year_month(token: str):
    """Turn '07/2024', 'July 2024', or '2024' into a (year, month) pair."""
    token = token.strip()
    if token.lower() in ("present", "current", "now", "ongoing"):
        today = date.today()
        return today.year, today.month
    m = re.match(r"(\d{1,2})/(\d{4})", token)
    if m:
        return int(m.group(2)), int(m.group(1))
    m = re.match(r"([A-Za-z]{3,9})\.?\s+(\d{4})", token)
    if m:
        month = _MONTHS.get(m.group(1).lower()[:3], 1)
        return int(m.group(2)), month
    m = re.match(r"(\d{4})", token)
    if m:
        return int(m.group(1)), 1  # bare year — assume January
    return None


def resume_years(text: str) -> float:
    """
    Total professional experience, computed only from date ranges found
    inside the Experience / Professional Experience section:
      - different years  -> duration = end_year - start_year
      - same year         -> duration = (end_month - start_month) / 12
    Each range's duration goes into a list; the total is the sum.
    Falls back to a stated figure ('5+ years') only if no Experience
    section is found, or it contains no parseable date ranges.
    """
    section = experience_section(text)
    if not section:
        matches = re.findall(r"(\d+)\s*\+?\s*(?:years|yrs)", text, re.IGNORECASE)
        return float(max((int(m) for m in matches), default=0))

    durations = []
    for start_tok, end_tok in _DATE_RANGE_RE.findall(section):
        start = _to_year_month(start_tok)
        end = _to_year_month(end_tok)
        if not start or not end:
            continue
        start_year, start_month = start
        end_year, end_month = end
        if (end_year, end_month) <= (start_year, start_month):
            continue
        if end_year != start_year:
            durations.append(end_year - start_year)
        else:
            durations.append((end_month - start_month) / 12)

    if durations:
        return round(sum(durations), 1)

    matches = re.findall(r"(\d+)\s*\+?\s*(?:years|yrs)", text, re.IGNORECASE)
    return float(max((int(m) for m in matches), default=0))


def grade(score: float) -> str:
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"


# ---------- main scorer ----------

def match(resume_text: str, jd_text: str) -> dict:
    resume_skills = get_skills(resume_text)
    jd_skills = get_skills(jd_text)
    weights = skill_weights(jd_text, jd_skills)

    matched = sorted(set(resume_skills) & set(jd_skills))
    missing = sorted(set(jd_skills) - set(resume_skills))

    total_weight = sum(weights.values()) or 1
    matched_weight = sum(weights[s] for s in matched)
    skill_coverage = matched_weight / total_weight

    text_sim = similarity(resume_text, jd_text)
    verbs = verb_score(resume_text)
    quant = quant_ratio(resume_text)
    title = title_match(resume_text, jd_text)
    soft_jd, soft_resume = soft_skills(jd_text), soft_skills(resume_text)
    soft_overlap = (len(soft_jd & soft_resume) / len(soft_jd)) if soft_jd else 1.0

    yrs_required, yrs_have = jd_years(jd_text), resume_years(resume_text)
    if yrs_required == 0:
        years_modifier = 0
    elif yrs_have >= yrs_required:
        years_modifier = 5
    else:
        years_modifier = -5 * min((yrs_required - yrs_have) / max(yrs_required, 1), 1)

    score = 100 * (
        0.45 * skill_coverage +
        0.20 * text_sim +
        0.10 * title +
        0.10 * verbs +
        0.10 * quant +
        0.05 * soft_overlap
    ) + years_modifier
    score = round(max(0, min(100, score)))

    missing_ranked = sorted(missing, key=lambda s: -weights.get(s, 0))

    return {
        "score": score,
        "grade": grade(score),
        "metrics": {
            "skill_coverage_pct": round(skill_coverage * 100, 1),
            "text_similarity_pct": round(text_sim * 1, 1),
            "title_match_pct": round(title * 100, 3),
            "action_verb_strength_pct": round(verbs * 100, 1),
            "quantified_bullets_pct": round(quant * 100, 1),
            "soft_skill_overlap_pct": round(soft_overlap * 100, 1),
        },
        "experience": {
            "years_required": yrs_required,
            "years_in_resume": yrs_have,
        },
        "matched_skills": matched,
        "missing_skills_ranked": missing_ranked,
        "tailoring_notes": [
            f"Add or surface '{s}' — weighted {weights.get(s)}/3 urgency in the JD"
            for s in missing_ranked[:8]
        ],
    }


# ---------- JD scraping ----------

def fetch_jd(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; TsehayBot/1.0)"}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
        tag.decompose()

    candidates = soup.find_all(
        lambda t: t.name in ("div", "section", "article")
        and t.get("class")
        and any("description" in c.lower() or "job" in c.lower() for c in t.get("class"))
    )
    container = max(candidates, key=lambda t: len(t.get_text()), default=None) if candidates else None
    target = container if container else soup.body or soup

    text = target.get_text(separator="\n")
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


# ---------- CLI ----------

def analyze(resume_path: str, jd_path: str = None, jd_url: str = None) -> dict:
    resume_text = open(resume_path, encoding="utf-8").read()
    jd_text = fetch_jd(jd_url) if jd_url else open(jd_path, encoding="utf-8").read()
    result = match(resume_text, jd_text)
    result["jd_source"] = jd_url if jd_url else jd_path
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Score a resume against a job description — free, local, no API")
    parser.add_argument("resume", help="Path to resume .txt file")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--jd", help="Path to job description .txt file")
    group.add_argument("--jd-url", help="URL of a live job posting to scrape")
    args = parser.parse_args()

    output = analyze(args.resume, jd_path=args.jd, jd_url=args.jd_url)
    print(json.dumps(output, indent=2))
    