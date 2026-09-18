import requests

url = "https://jobs.telusdigital.com/search/jobs/in?cfm5=AI+Community&ns_category=ai-community"

response = requests.get(url, timeout=10)

print(response.status_code)
print(response.url)
print(len(response.text))