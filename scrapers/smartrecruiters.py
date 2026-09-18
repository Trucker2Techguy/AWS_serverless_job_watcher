import requests
from bs4 import BeautifulSoup
import json




def download_page(url):
    """Download a SmartRecruiters career page"""

    try:

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response

    except requests.RequestException as error:
        print(f"Unable to download page: {error}")
        return None

def get_jobs(url):
    """Download a SmartRecruiters career page and reuturn its current job listings"""

    response = download_page(url)

    if response is None:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

    jobs = []

    for link in links:
        href = link.get("href")

        if href and "jobs.smartrecruiters.com/Resultant" in href:
            job = {
                "title": link.text.strip(),
                "url": href

            }
            jobs.append(job)
    return jobs

def filter_jobs(jobs, keywords):
    """Filter jobs who's title matches at least one keyword"""
    matching_jobs = []

    for job in jobs:
        title = job["title"].lower()

        for keyword in keywords:
            if keyword.lower() in title:
                matching_jobs.append(job)
                break
    return matching_jobs

def load_seen_jobs():
    """Load seen jobs from JSON file"""
    try:
        with open("seen_jobs.json", "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return []


url = "https://www.smartrecruiters.com/Resultant"
#
# jobs = get_jobs(url)
#
# seen_jobs = load_seen_jobs()
#
def get_new_jobs(matching_jobs, seen_jobs):
    """Retuern matching jobs that have not been seen before"""

    seen_urls = []

    for job in seen_jobs:
        seen_urls.append(job["url"])

    new_jobs = []

    for job in matching_jobs:
        if job["url"] not in seen_urls:
            new_jobs.append(job)

    return new_jobs

def save_seen_jobs(seen_jobs, new_jobs):
    """Save previously seen plus newly discovered jobs"""

    all_seen_jobs = seen_jobs + new_jobs

    with open("seen_jobs.json", "w", encoding="utf-8") as file:
        json.dump(all_seen_jobs, file, indent=4)
#
#
# print(f"Previously seen jobs: {len(seen_jobs)}")
# keywords = [
#     "system",
#     "network",
#     "cloud",
#     "support"
# ]
#
#
# matching_jobs = filter_jobs(jobs, keywords)
#
# new_jobs = get_new_jobs(matching_jobs, seen_jobs)
#
# for job in new_jobs:
#     print(job["title"])
#     print(job["url"])
#
#
# save_seen_jobs(seen_jobs, new_jobs)