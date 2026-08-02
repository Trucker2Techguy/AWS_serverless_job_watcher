import json

from scrapers.hrmdirect import download_page, get_jobs, inspect_html


CONFIG_FILE = "config/companies.json"


def load_companies():
    """Load company configuration from the JSON file."""

    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    print("AWS Job Watcher")
    print("-" * 20)

    companies = load_companies()

    for company in companies:
        company_name = company["company"]
        company_url = company["url"]

        print(f"\nChecking {company_name}")
        print(company_url)

        if company_name == "Novelty Inc.":
            #jobs = get_jobs(company_url)
            response = download_page(company_url)
            if response is not None:
                inspect_html(response.text)
                print("Saved HTML to novelty_page.html")

            #print(f"Found {len(jobs)} links")

            #for job in jobs:
            #   print(job["title"])
            #   print(job["url"])

if __name__ == "__main__":
    main()