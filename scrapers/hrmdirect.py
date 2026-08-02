import requests
from bs4 import BeautifulSoup


def download_page(url):
    """Download a webpage and return the HTTP response."""

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response

    except requests.RequestException as error:
        print(f"Unable to download page: {error}")
        return None


def get_page_title(html):
    """Extract the title from the downloaded HTML."""

    soup = BeautifulSoup(html, "html.parser")

    if soup.title:
        return soup.title.get_text(strip=True)

    return "No title found"

def get_jobs(url):
    """Download an HR Direct careers page and return its job listings."""

    response = download_page(url)

    if response is None:
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []

    # Temporary: inspect every link that might be a job posting.
    for link in soup.find_all("a", href=True):
        title = link.get_text(strip=True)
        job_url = link["href"]

        if title:
            jobs.append(
                {
                    "title": title,
                    "url": job_url
                }
            )

    return jobs

def inspect_html(html):
    """Save downloaded HTML so it can be inspected locally."""

    with open("novelty_page.html", "w", encoding="utf-8") as file:
        file.write(html)