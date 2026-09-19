import json
import boto3
import os


# from scrapers.hrmdirect import download_page, get_jobs, inspect_html
from scrapers.smartrecruiters import (
    get_jobs as get_smartrecruiters_jobs,
    filter_jobs
)
from scrapers.gig_jobs import get_gig_jobs
from scrapers.dataannotation import get_dataannotation_jobs

# session = boto3.Session(profile_name="job-watcher") """test enviroment"""

if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    session = boto3.Session()
else:
    session = boto3.Session(profile_name="job-watcher")

dynamodb = session.resource("dynamodb")
sns = session.client("sns")

gig_table = dynamodb.Table("job-watcher-seen-gigs")
job_table = dynamodb.Table("job-watcher-seen-jobs")

SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:178504705772:aws-job-watcher-alerts" #"""Use your own SNS topic ARN"""

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
    all_new_jobs = new_dynamodb_gig_jobs.copy()




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
            new_jobs = []

            for job in matching_jobs:
                response = job_table.get_item(
                    Key={"url": job["url"]}
                )

                if "Item" not in response:
                    print(f"New employer job: {job['title']}")
                    new_jobs.append(job)
                    job_table.put_item(Item=job)

            print(f"New jobs: {len(new_jobs)}")

            all_new_jobs.extend(new_jobs)

            print(f"Found {len(jobs)} jobs.")
            print(f"Matched {len(matching_jobs)} jobs.")




            #print(f"Found {len(jobs)} links")

            #for job in jobs:
            #   print(job["title"])
            #   print(job["url"])

    print(f"\nTotal new jobs across all sources: {len(all_new_jobs)}")
    send_job_alerts(all_new_jobs)
def find_new_gig_jobs(all_gig_jobs):
    new_dynamodb_gig_jobs = []

def send_job_alerts(jobs):
    if not jobs:
        print("No new jobs to email.")
        return

    message_lines = [
        f"AWS Job Watcher found {len(jobs)} new job(s):",
        ""
    ]

    for job in jobs:
        message_lines.append(job["title"])
        message_lines.append(job["url"])
        message_lines.append("")

    message = "\n".join(message_lines)

    response = sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"AWS Job Watcher - {len(jobs)} New Job(s)",
        Message=message
    )

    print(f"SNS Message ID: {response['MessageId']}")

def lambda_handler(event, context):
    main()

    return {
        "statusCode": 200,
        "body": "AWS Job Watcher completed successfully."
    }


if __name__ == "__main__":
    main()