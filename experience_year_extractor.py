import re
from datetime import datetime


def extract_required_experience(job_description):
    """
    Extract the minimum years of experience
    required by the job description.
    """

    if not job_description:
        return 0

    patterns = [
        # Example:
        # "2+ years of professional software development experience"
        # "3 years of backend development experience"
        r'(\d+)\+?\s*years?\s+(?:of\s+)?(?:[\w]+\s+){0,8}experience',

        # Example:
        # "minimum 2 years"
        # "at least 3 years"
        r'(?:minimum|at\s+least)\s+(\d+)\s*years?'
    ]

    description = job_description.lower()

    for pattern in patterns:
        match = re.search(pattern, description)

        if match:
            return int(match.group(1))

    return 0


def extract_experience_section(resume):
    """
    Extract only the professional/work experience
    section from the resume.
    """

    if not resume:
        return ""

    experience_pattern = (
        r'\b(?:professional\s+experience|'
        r'work\s+experience|'
        r'work\s+history|'
        r'employment\s+history|'
        r'career\s+history|'
        r'professional\s+background|'
        r'experience)\b'
    )

    next_section_pattern = (
        r'\b(?:education|'
        r'projects|'
        r'skills|'
        r'certifications|'
        r'awards|'
        r'languages|'
        r'summary|'
        r'profile|'
        r'references|'
        r'achievements|'
        r'volunteer\s+experience)\b'
    )

    experience_match = re.search(
        experience_pattern,
        resume,
        re.IGNORECASE
    )

    if not experience_match:
        return ""

    experience_start = experience_match.end()

    remaining_resume = resume[experience_start:]

    next_section_match = re.search(
        next_section_pattern,
        remaining_resume,
        re.IGNORECASE
    )

    if next_section_match:
        experience_end = next_section_match.start()

        return remaining_resume[:experience_end]

    return remaining_resume


def extract_experience_months(experience_section):
    """
    Extract job date ranges and calculate total
    professional experience in months.

    Overlapping jobs are merged so that the same
    period is not counted twice.
    """

    if not experience_section:
        return 0

    pattern = (
        r'(\d{1,2})/(\d{2,4})'
        r'\s*[-–]'
        r'\s*'
        r'(?:(\d{1,2})/(\d{2,4})|(Present))'
    )

    matches = re.findall(
        pattern,
        experience_section,
        re.IGNORECASE
    )

    experience_periods = []

    for (
        start_month,
        start_year,
        end_month,
        end_year,
        present
    ) in matches:

        start_month = int(start_month)
        start_year = int(start_year)

        if start_year < 100:
            start_year += 2000

        start_total_months = (
            start_year * 12 + start_month
        )

        if present:
            now = datetime.now()

            end_total_months = (
                now.year * 12 + now.month
            )

        else:
            end_month = int(end_month)
            end_year = int(end_year)

            if end_year < 100:
                end_year += 2000

            end_total_months = (
                end_year * 12 + end_month
            )

        if end_total_months >= start_total_months:
            experience_periods.append(
                (
                    start_total_months,
                    end_total_months
                )
            )

    if not experience_periods:
        return 0

    # Sort periods by start date.
    experience_periods.sort()

    # Merge overlapping periods.
    merged_periods = [experience_periods[0]]

    for current_start, current_end in experience_periods[1:]:

        previous_start, previous_end = merged_periods[-1]

        if current_start <= previous_end:
            merged_periods[-1] = (
                previous_start,
                max(previous_end, current_end)
            )

        else:
            merged_periods.append(
                (
                    current_start,
                    current_end
                )
            )

    total_months = 0

    for start, end in merged_periods:
        total_months += end - start

    return total_months


def months_to_years_months(total_months):
    """
    Convert total months into years and months.
    """

    years = total_months // 12
    months = total_months % 12

    return years, months


def calculate_experience_score(
    candidate_months,
    required_years
):
    """
    Calculate how much of the required experience
    the candidate satisfies.
    """

    required_months = required_years * 12

    if required_months == 0:
        return 100

    score = (
        candidate_months / required_months
    ) * 100

    return min(score, 100)


def experience_matcher(resume, job_description):
    """
    Main experience matching function.

    Extracts the candidate's experience,
    extracts the job's required experience,
    calculates the score, and returns the result.
    """

    experience_section = extract_experience_section(
        resume
    )

    candidate_months = extract_experience_months(
        experience_section
    )

    required_years = extract_required_experience(
        job_description
    )

    score = calculate_experience_score(
        candidate_months,
        required_years
    )

    candidate_years, remaining_months = (
        months_to_years_months(candidate_months)
    )

    return {
        "score": score,
        "candidate_months": candidate_months,
        "candidate_years": candidate_years,
        "candidate_remaining_months": remaining_months,
        "required_years": required_years
    }