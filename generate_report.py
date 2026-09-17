from skill_extraction import extract_skills, similarity_score, skills
from responsibilities_matching import responsiblity_matcher
from experience_year_extractor import extract_experience_section, extract_experience_months, months_to_years_months, extract_required_experience, calculate_experience_score
from extract_responsiblity import extract_responsibilities
from education_matcher import education_matcher, extract_education_section, extract_required_degrees, extract_candidate_degrees, degree_fields
from skill_extraction import skill_matcher
def generate_match_report(resume, job_description):

    # -----------------------------------
    # 1. SKILLS
    # -----------------------------------

    skill_result = skill_matcher(
        resume,
        job_description
    )

    skill_score = skill_result["score"]
    matched_skills = skill_result["matched"]
    missing_skills = skill_result["missing"]
    required_skills = skill_result["required"]


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

    responsibility_score = responsiblity_matcher(
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
    # 6. SKILL EXPLANATION
    # -----------------------------------

    if not missing_skills:

        skill_explanation = (
            "Your resume contains all detected "
            "skills from the job description."
        )

    else:

        skill_explanation = (
            "Your resume is missing these detected "
            "job skills: "
            + ", ".join(missing_skills)
            + ". If you genuinely have experience "
              "with these skills, consider adding them "
              "to your resume."
        )


    # -----------------------------------
    # 7. EXPERIENCE EXPLANATION
    # -----------------------------------

    if required_years == 0:

        experience_explanation = (
            "The job description does not specify "
            "a minimum experience requirement."
        )

    elif experience_score >= 100:

        experience_explanation = (
            f"Your detected professional experience "
            f"is {candidate_years} years and "
            f"{candidate_months} months, which meets "
            f"the stated requirement of "
            f"{required_years} years."
        )

    else:

        experience_explanation = (
            f"Your detected professional experience "
            f"is {candidate_years} years and "
            f"{candidate_months} months, while the "
            f"job requires {required_years} years."
        )


    # -----------------------------------
    # 8. RESPONSIBILITY EXPLANATION
    # -----------------------------------

    if responsibility_score >= 70:

        responsibility_explanation = (
            "Your experience shows strong textual "
            "similarity to the responsibilities "
            "described in the job."
        )

    elif responsibility_score > 0:

        responsibility_explanation = (
            "Your experience has some similarity to "
            "the job responsibilities, but some "
            "relevant responsibilities may not be "
            "clearly represented in your resume."
        )

    else:

        responsibility_explanation = (
            "Your resume does not show strong textual "
            "similarity to the detected job responsibilities."
        )


    # -----------------------------------
    # 9. EDUCATION EXPLANATION
    # -----------------------------------

    if not required_degrees:

        education_explanation = (
            "The job description does not specify "
            "a recognized degree requirement."
        )

    elif education_score == 100:

        education_explanation = (
            "Your detected education matches the "
            "detected degree requirements."
        )

    elif candidate_degrees:

        education_explanation = (
            "Your education matches some of the "
            "degree fields detected in the job "
            "description, but not all of them."
        )

    else:

        education_explanation = (
            "No matching degree field was detected "
            "in your Education section."
        )


    # -----------------------------------
    # 10. FINAL REPORT
    # -----------------------------------

    return {

        "overall_score": round(
            overall_score,
            2
        ),

        "skills": {
            "score": round(
                skill_score,
                2
            ),
            "matched": matched_skills,
            "missing": missing_skills,
            "explanation": skill_explanation,
            "required_skills": required_skills
        },

        "experience": {
            "score": round(
                experience_score,
                2
            ),
            "candidate_experience": (
                f"{candidate_years} years "
                f"{candidate_months} months"
            ),
            "required_experience": required_years,
            "explanation": experience_explanation
        },

        "responsibilities": {
            "score": round(
                responsibility_score,
                2
            ),
            "explanation": responsibility_explanation
        },

        "education": {
            "score": round(
                education_score,
                2
            ),
            "matched": candidate_degrees,
            "required": required_degrees,
            "explanation": education_explanation
        }
    }