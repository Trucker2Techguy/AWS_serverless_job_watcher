import requests
from bs4 import BeautifulSoup

def get_dataannotation_jobs():

    url = "https://www.dataannotation.tech/"

    response = requests.get(url, timeout=10)

    # print(response.status_code)
    # print(response.url)
    # print(len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")

#    print(f"Found {len(links)} links")

    keywords = [
        "software",
        "engineer",
        "data",
        "python",
        "cloud",
        "technical",
    #    "AI",
    ]

    jobs = []

    for link in links:
        title = link.get_text(" ", strip=True)
        href = link.get("href")

        if href and href.startswith("/job-board"):

            for keyword in keywords:
                if keyword.lower() in title.lower():
                    full_url = "https://www.dataannotation.tech" + href

                    job = {
                        "title": title,
                        "url": full_url
                    }

                    jobs.append(job)
                    # print(title)
                    # print(link.get("href"))
                    break

    print(f"Found {len(jobs)} matching jobs")

    #
    # print(jobs[0])
    return jobs

# get_dataannotation_jobs()