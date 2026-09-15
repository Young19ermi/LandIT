import re
from datetime import datetime


def extract_required_experience(job_description):

    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'(?:minimum|at\s+least)\s+(\d+)\s*years?'
    ]

    description = job_description.lower()

    for pattern in patterns:
        match = re.search(pattern, description)

        if match:
            return int(match.group(1))

    return 0


def extract_experience_section(resume):

    experience_pattern = (
        r'\b(?:professional\s+experience|work\s+experience|'
        r'work\s+history|employment\s+history|'
        r'career\s+history|professional\s+background|'
        r'experience)\b'
    )

    next_section_pattern = (
        r'\b(?:education|projects|skills|'
        r'certifications|awards|languages|'
        r'summary|profile|references|'
        r'achievements|volunteer\s+experience)\b'
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
                (start_total_months, end_total_months)
            )

    if not experience_periods:
        return 0

    # Sort periods by start date
    experience_periods.sort()

    # Start with the first period
    merged_periods = [experience_periods[0]]

    for current_start, current_end in experience_periods[1:]:

        previous_start, previous_end = merged_periods[-1]

        # Overlapping or directly connected periods
        if current_start <= previous_end:
            merged_periods[-1] = (
                previous_start,
                max(previous_end, current_end)
            )

        else:
            merged_periods.append(
                (current_start, current_end)
            )

    # Calculate total months after merging
    total_months = 0

    for start, end in merged_periods:
        total_months += end - start

    return total_months

def months_to_years_months(total_months):

    years = total_months // 12
    months = total_months % 12

    return years, months


def calculate_experience_score(
    candidate_months,
    required_years
):

    required_months = required_years * 12

    if required_months == 0:
        return 100

    score = (
        candidate_months / required_months
    ) * 100

    return min(score, 100)