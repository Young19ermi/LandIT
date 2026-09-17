import argparse
import os

from Job_fetcher import fetch_job_description
from generate_report import generate_match_report


resume = """
John Doe
Software Engineer

PROFESSIONAL EXPERIENCE

Software Engineer | Tech Solutions
01/2023 - Present

- Developed web applications using Python, React, and JavaScript.
- Built REST APIs using Node.js and Express.
- Worked with PostgreSQL and MongoDB databases.
- Used Git and GitHub for version control.
- Collaborated with the team using Agile practices.
- Designed responsive user interfaces with Tailwind.

Junior Software Developer | Web Company
06/2021 - 12/2022

- Developed frontend features using React and JavaScript.
- Built backend services using Node.js.
- Worked with REST APIs and PostgreSQL.
- Participated in code reviews.

EDUCATION

BSc in Computer Science
Addis Ababa University
2017 - 2021

SKILLS

Python, JavaScript, React, Node.js, Express, PostgreSQL,
MongoDB, Git, GitHub, Tailwind, REST API
"""


def get_job_description(source):
    """
    Get the job description from either a local
    text file or a job posting URL.
    """

    if os.path.isfile(source):

        with open(
            source,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()

    return fetch_job_description(source)


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Find the best matching jobs "
            "for your resume."
        )
    )

    parser.add_argument(
        "--jd",
        action="append",
        required=True,
        help=(
            "Job posting URL or path to a "
            "job description text file. "
            "Can be used multiple times."
        )
    )

    args = parser.parse_args()

    job_results = []

    for source in args.jd:

        try:

            job_description = get_job_description(
                source
            )

            report = generate_match_report(
                resume,
                job_description
            )

            job_results.append({
                "source": source,
                "report": report
            })

        except Exception as error:

            print(
                f"\nCould not process: {source}"
            )

            print(
                f"Error: {error}"
            )

    if not job_results:

        print("\nNo jobs could be processed.")

        return

    # Sort jobs by overall score.
    job_results.sort(
        key=lambda job: (
            job["report"]["overall_score"]
        ),
        reverse=True
    )

    # Only show the top 3.
    top_jobs = job_results[:3]

    print("\n================================")
    print("       TOP JOB MATCHES")
    print("================================")

    for index, job in enumerate(
        top_jobs,
        start=1
    ):

        report = job["report"]
        source = job["source"]

        print(f"\n#{index}")

        # Show whether the source was a file or URL.
        if os.path.isfile(source):

            print(f"File: {source}")

        else:

            print(f"URL: {source}")

        print(
            f"Overall Score: "
            f"{report['overall_score']}%"
        )

        print("\n--- SKILLS ---")

        print(
            f"Score: "
            f"{report['skills']['score']}%"
        )

        print(
            "Matched:",
            ", ".join(
                report["skills"]["matched"]
            )
            if report["skills"]["matched"]
            else "None"
        )

        print(
            "Missing:",
            ", ".join(
                report["skills"]["missing"]
            )
            if report["skills"]["missing"]
            else "None"
        )

        print(
            "Skills Expected:",
            report["skills"]["required_skills"]
        )

        print(
            "Explanation:",
            report["skills"]["explanation"]
        )

        print("\n--- EXPERIENCE ---")

        print(
            f"Score: "
            f"{report['experience']['score']}%"
        )

        print(
            "Candidate:",
            report["experience"]["candidate_experience"]
        )

        print(
            "Required:",
            f"{report['experience']['required_experience']} years"
        )

        print(
            "Explanation:",
            report["experience"]["explanation"]
        )

        print("\n--- RESPONSIBILITIES ---")

        print(
            f"Score: "
            f"{report['responsibilities']['score']}%"
        )

        print(
            "Explanation:",
            report["responsibilities"]["explanation"]
        )

        print("\n--- EDUCATION ---")

        print(
            f"Score: "
            f"{report['education']['score']}%"
        )

        print(
            "Candidate:",
            ", ".join(
                report["education"]["matched"]
            )
            if report["education"]["matched"]
            else "None"
        )

        print(
            "Required:",
            ", ".join(
                report["education"]["required"]
            )
            if report["education"]["required"]
            else "None"
        )

        print(
            "Explanation:",
            report["education"]["explanation"]
        )


if __name__ == "__main__":
    main()