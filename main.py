import json

# from scrapers.hrmdirect import download_page, get_jobs, inspect_html
from scrapers.smartrecruiters import (get_jobs as get_smartrecruiters_jobs,
    filter_jobs, load_seen_jobs, get_new_jobs, save_seen_jobs)
from scrapers.gig_jobs import get_gig_jobs
from scrapers.dataannotation import get_dataannotation_jobs



CONFIG_FILE = "config/companies.json"


def load_companies():
    """Load company configuration from the JSON file."""

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("AWS Job Watcher")
    print("-" * 20)

    gig_jobs = get_gig_jobs()
    dataannotation_jobs = get_dataannotation_jobs()

    print(f"Main received {len(dataannotation_jobs)} DataAnnotation jobs")
    print(f"Main received {len(gig_jobs)} gig jobs")

    all_gig_jobs = gig_jobs + dataannotation_jobs
    print(f"Total gig jobs: {len(all_gig_jobs)}")

    with open("seen_gig_jobs.json", "r", encoding="utf-8") as file:
        seen_gig_jobs = json.load(file)

    print(f"Previously seen gig jobs: {len(seen_gig_jobs)}")




    seen_gig_urls = []

    for job in seen_gig_jobs:
        seen_gig_urls.append(job["url"])

    new_gig_jobs = []

    for job in all_gig_jobs:
        if job["url"] not in seen_gig_urls:
            new_gig_jobs.append(job)

    print(f"New gig jobs: {len(new_gig_jobs)}")

    for job in new_gig_jobs:
        print(job["title"])
        print(job["url"])

    all_seen_gig_jobs = seen_gig_jobs + new_gig_jobs

    with open("seen_gig_jobs.json", "w", encoding="utf-8") as file:
        json.dump(all_seen_gig_jobs, file, indent=4)

    companies = load_companies()

    for company in companies:
        company_name = company["company"]
        company_url = company["url"]

        print(f"\nChecking {company_name}")
        print(company_url)


        if company_name == "Resultant":
            jobs = get_smartrecruiters_jobs(company_url)
            keywords = company["keywords"]
            matching_jobs = filter_jobs(jobs, keywords)
            seen_jobs = load_seen_jobs()
            new_jobs = get_new_jobs(matching_jobs, seen_jobs)
            print (f"Previous seen jobs: {len(seen_jobs)}")
            print(f"New jobs: {len(new_jobs)}")

            print(f"Found {len(jobs)} jobs.")
            print(f"Matched {len(matching_jobs)} jobs.")



            #print(f"Found {len(jobs)} links")

            #for job in jobs:
            #   print(job["title"])
            #   print(job["url"])

if __name__ == "__main__":
    main()