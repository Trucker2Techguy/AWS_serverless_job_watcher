import requests
from bs4 import BeautifulSoup

def get_gig_jobs():

    url = "https://jobs.lever.co/appen"

    response = requests.get(url, timeout =10)


    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")


    keywords = [
        "AI",
        "data",
        "evaluator",
        "python",
        "cloud",
        "technical",
    ]

    jobs = []


    for link in links:
        href = link.get("href")
        title = link.get_text(" ", strip=True)

        if href and "jobs.lever.co/appen/" in href and title != "Apply" and "United States" in title:
            for keyword in keywords:
                if keyword.lower() in title.lower():

                    job = {
                        "title": title,
                        "url": href

                    }

                    jobs.append(job)
                    # print(title)
                    # print(href)
                    break

    print(f"Found {len(jobs)} matching Appen jobs")

    return jobs

