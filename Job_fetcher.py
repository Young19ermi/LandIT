import requests
from bs4 import BeautifulSoup


def fetch_job_description(url):
    """
    Fetch a job posting from a URL and return
    the text content of the page.
    """

    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove elements that are not useful job content.
    for element in soup(
        ["script", "style", "nav", "footer", "header"]
    ):
        element.decompose()

    job_description = soup.get_text(
        separator="\n"
    )

    return job_description