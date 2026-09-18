import json
import boto3


# from scrapers.hrmdirect import download_page, get_jobs, inspect_html
from scrapers.smartrecruiters import (get_jobs as get_smartrecruiters_jobs,
    filter_jobs, load_seen_jobs, get_new_jobs, save_seen_jobs)
from scrapers.gig_jobs import get_gig_jobs
from scrapers.dataannotation import get_dataannotation_jobs

dynamodb = boto3.Session(profile_name="job-watcher").resource("dynamodb")
gig_table = dynamodb.Table("job-watcher-seen-gigs")


CONFIG_FILE = "config/companies.json"


def load_companies():
    """Load company configuration from the JSON file."""

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("AWS Job Watcher")
    print("-" * 20)

   # print(gig_table.table_status)




    gig_jobs = get_gig_jobs()
    dataannotation_jobs = get_dataannotation_jobs()

    print(f"Main received {len(dataannotation_jobs)} DataAnnotation jobs")
    print(f"Main received {len(gig_jobs)} gig jobs")

    all_gig_jobs = gig_jobs + dataannotation_jobs
    print(f"Total gig jobs: {len(all_gig_jobs)}")

    new_dynamodb_gig_jobs = []

    for job in all_gig_jobs:
        # print(test_job)

        response = gig_table.get_item(
            Key={"url": job["url"]}
        )

        if "Item" not in response:
            print("Real job is new")
            new_dynamodb_gig_jobs.append(job)
            gig_table.put_item(Item=job)

    print(f"New DynamoDB gig jobs: {len(new_dynamodb_gig_jobs)}")




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

def find_new_gig_jobs(all_gig_jobs):
    new_dynamodb_gig_jobs = []

if __name__ == "__main__":
    main()