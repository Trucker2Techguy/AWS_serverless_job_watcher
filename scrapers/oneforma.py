import json

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.oneforma.com/projects/"


def get_project_details(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    details = {
        "countries": [],
        "languages": [],
        "worldwide": False,
        "description": "",
        "date_posted": None,
        "employment_type": None
    }

    # First choice: structured JobPosting JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            if not script.string:
                continue

            data = json.loads(script.string)

            if not isinstance(data, dict):
                continue

            if data.get("@type") != "JobPosting":
                continue

            details["date_posted"] = data.get("datePosted")
            details["employment_type"] = data.get("employmentType")

            description = data.get("description", "")
            description_soup = BeautifulSoup(description, "html.parser")

            details["description"] = description_soup.get_text(
                " ",
                strip=True
            )

            # Extract countries from structured jobLocation data
            for location in data.get("jobLocation", []):
                if not isinstance(location, dict):
                    continue

                address = location.get("address", {})

                if not isinstance(address, dict):
                    continue

                country = address.get("addressCountry")

                if country:
                    details["countries"].append(country)

            # Extract explicit language requirements
            for item in description_soup.find_all("li"):
                text = item.get_text(" ", strip=True)

                if text.startswith("Languages:"):
                    language_text = text.replace(
                        "Languages:",
                        "",
                        1
                    ).strip()

                    details["languages"] = [
                        language.strip()
                        for language in language_text.split(",")
                    ]

                    break

            return details

        except (json.JSONDecodeError, TypeError):
            continue


    # Fallback for pages without JobPosting JSON-LD
    page_text = soup.get_text(" ", strip=True)

    details["description"] = page_text

    # Look specifically for location/eligibility information
    for item in soup.find_all(["li", "div", "p"]):
        text = item.get_text(" ", strip=True)

        if (
                "Location" in text
                or "applicant eligibility" in text.lower()
        ):
            if "Worldwide" in text:
                details["worldwide"] = True
                break

    return details

def evaluate_project(job):
    # Must be available in the US or worldwide
    us_eligible = (
        "US" in job["countries"]
        or job["worldwide"]
    )

    if not us_eligible:
        return False, "Not US/Worldwide"

    # If languages are explicitly listed,
    # English must be one of them.
    if (
        job["languages"]
        and "English" not in job["languages"]
    ):
        return False, "Explicit non-English language"

    title = job["title"].lower()

    # Work we do NOT want
    exclude_keywords = [
        "video",
        "audio",
        "transcription",
        "phone call",
        "conversation",
        "translation",
        "translator",
        "health record",
        "data sharing",
        "email data",
        "recorder"
    ]

    for keyword in exclude_keywords:
        if keyword in title:
            return False, f"Excluded keyword: {keyword}"

    # Work we're actually interested in
    include_keywords = [
        "ai",
        "annotation",
        "annotator",
        "evaluator",
        "evaluation",
        "quality",
        "relevance",
        "labeling",
        "search",
        "rubric",
        "prompt"
    ]

    for keyword in include_keywords:
        if keyword in title:
            return True, f"Matched keyword: {keyword}"

    return False, "No relevant keyword"




def get_oneforma_jobs(seen_table=None):
    project_links = {}

    page = 1

    while True:
        if page == 1:
            url = BASE_URL
        else:
            url = f"{BASE_URL}page/{page}/"

        print(f"Checking OneForma page {page}")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        projects_before = len(project_links)

        for link in soup.find_all("a", href=True):
            href = link["href"]
            text = link.get_text(" ", strip=True)

            if (
                href.startswith(BASE_URL)
                and href != BASE_URL
                and "/page/" not in href
                and text
                and text != "Apply"
            ):
                project_links[href] = text

        if len(project_links) == projects_before:
            print(
                f"No new projects found on page {page}. "
                "Stopping."
            )
            break

        page += 1

    jobs = []

    already_evaluated = 0
    new_projects = 0

    for url, title in project_links.items():

        # Skip projects we've already evaluated
        if seen_table is not None:
            response = seen_table.get_item(
                Key={"url": url}
            )

            if "Item" in response:
                already_evaluated += 1
                continue

        new_projects += 1

        print(f"Evaluating new project: {title}")

        details = get_project_details(url)

        job = {
            "title": title,
            "url": url,
            "countries": details["countries"],
            "languages": details["languages"],
            "worldwide": details["worldwide"],
            "description": details["description"],
            "date_posted": details["date_posted"],
            "employment_type": details["employment_type"]
        }

        relevant, reason = evaluate_project(job)

        print(f"  Relevant: {relevant} ({reason})")

        if relevant:
            jobs.append(job)

        # Remember that we've evaluated this URL,
        # whether it was relevant or rejected.
        if seen_table is not None:
            seen_table.put_item(
                Item={
                    "url": url,
                    "title": title
                }
            )

    print(f"Already evaluated: {already_evaluated}")
    print(f"New projects evaluated: {new_projects}")
    print(f"Relevant new projects: {len(jobs)}")

    return jobs

if __name__ == "__main__":
    import boto3

    session = boto3.Session(profile_name="job-watcher")
    dynamodb = session.resource("dynamodb")

    oneforma_seen_table = dynamodb.Table(
        "job-watcher-oneforma-seen"
    )

    jobs = get_oneforma_jobs(oneforma_seen_table)

    print("\n" + "=" * 60)
    print(f"NEW RELEVANT ONEFORMA PROJECTS: {len(jobs)}")

    for job in jobs:
        print(job["title"])
        print(job["url"])