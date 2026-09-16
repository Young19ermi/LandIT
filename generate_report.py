from skill_extraction import extract_skills, similarity_score, skills
from skill_extraction import skill
from experience_year_extractor import extract_experience_section, extract_experience_months, months_to_years_months, extract_required_experience, calculate_experience_score
from extract_responsiblity import extract_responsibilities, responsibilities_similarity
from education_matcher import education_matcher, extract_education_section, extract_required_degrees, extract_candidate_degrees, degree_fields
def generate_match_report(resume, job_description):
    """
    Generate a complete resume-to-job match report.

    The report contains:
        - Overall score
        - Skill score and skill gap
        - Experience score
        - Responsibility score
        - Education score
        - Verbal explanation for each metric
    """

    # -----------------------------------
    # 1. SKILLS
    # -----------------------------------

    resume_skills = extract_skills(
        skills,
        resume
    )

    job_skills = extract_skills(
        skills,
        job_description
    )

    skill_score = similarity_score(
        resume_skills,
        job_skills
    )

    missing_skills = list(
        set(job_skills) - set(resume_skills)
    )

    matched_skills = list(
        set(resume_skills).intersection(
            set(job_skills)
        )
    )

    # -----------------------------------
    # 2. EXPERIENCE
    # -----------------------------------

    experience_section = extract_experience_section(
        resume
    )

    candidate_experience_months = extract_experience_months(
        experience_section
    )

    candidate_years, candidate_months = months_to_years_months(
        candidate_experience_months
    )

    required_years = extract_required_experience(
        job_description
    )

    experience_score = calculate_experience_score(
        candidate_experience_months,
        required_years
    )

    # -----------------------------------
    # 3. RESPONSIBILITIES
    # -----------------------------------

    job_responsibilities = extract_responsibilities(
        job_description
    )

    responsibility_score = responsibilities_similarity(
        experience_section,
        job_responsibilities
    )

    # -----------------------------------
    # 4. EDUCATION
    # -----------------------------------

    education_score = education_matcher(
        resume,
        job_description
    )

    education_section = extract_education_section(
        resume
    )

    required_degrees = extract_required_degrees(
        job_description,
        degree_fields
    )

    candidate_degrees = extract_candidate_degrees(
        education_section,
        degree_fields
    )

    # -----------------------------------
    # 5. OVERALL SCORE
    # -----------------------------------

    overall_score = (
        skill_score * 0.50
        + experience_score * 0.20
        + responsibility_score * 0.20
        + education_score * 0.10
    )

    # -----------------------------------
    # 6. VERBAL EXPLANATIONS
    # -----------------------------------

    if missing_skills:
        skill_explanation = (
            "Your resume is missing the following skills "
            "detected in the job description: "
            + ", ".join(missing_skills)
            + ". If you genuinely have experience with these "
              "skills, consider adding them to your resume."
        )
    else:
        skill_explanation = (
            "Your resume contains all of the detected "
            "skills required by the job description."
        )

    if required_years == 0:
        experience_explanation = (
            "The job description does not specify a minimum "
            "years-of-experience requirement."
        )
    elif experience_score >= 100:
        experience_explanation = (
            f"You have approximately {candidate_years} years "
            f"and {candidate_months} months of detected "
            f"professional experience, which meets or exceeds "
            f"the stated requirement of {required_years} years."
        )
    else:
        experience_explanation = (
            f"You have approximately {candidate_years} years "
            f"and {candidate_months} months of detected "
            f"professional experience, compared with the "
            f"required {required_years} years."
        )

    if responsibility_score >= 70:
        responsibility_explanation = (
            "Your professional experience shows strong "
            "similarity to the responsibilities described "
            "in the job description."
        )
    elif responsibility_score > 0:
        responsibility_explanation = (
            "Your professional experience has some similarity "
            "to the responsibilities in the job description, "
            "but some relevant responsibilities may not be "
            "clearly represented in your resume."
        )
    else:
        responsibility_explanation = (
            "Your resume does not show strong textual "
            "similarity to the responsibilities detected "
            "in the job description."
        )

    if not required_degrees:
        education_explanation = (
            "The job description does not specify a degree "
            "requirement."
        )
    elif education_score == 100:
        education_explanation = (
            "Your detected education matches all of the "
            "detected degree requirements."
        )
    elif candidate_degrees:
        education_explanation = (
            "Your resume matches some of the degree fields "
            "mentioned in the job description, but not all "
            "of the detected requirements."
        )
    else:
        education_explanation = (
            "No matching degree field was detected in your "
            "Education section."
        )

    # -----------------------------------
    # 7. RETURN COMPLETE REPORT
    # -----------------------------------

    return {
        "overall_score": round(overall_score, 2),

        "skills": {
            "score": round(skill_score, 2),
            "matched": matched_skills,
            "missing": missing_skills,
            "explanation": skill_explanation
        },

        "experience": {
            "score": round(experience_score, 2),
            "candidate_experience": (
                f"{candidate_years} years "
                f"{candidate_months} months"
            ),
            "required_experience": required_years,
            "explanation": experience_explanation
        },

        "responsibilities": {
            "score": round(responsibility_score, 2),
            "explanation": responsibility_explanation
        },

        "education": {
            "score": round(education_score, 2),
            "matched": candidate_degrees,
            "required": required_degrees,
            "explanation": education_explanation
        }
    }