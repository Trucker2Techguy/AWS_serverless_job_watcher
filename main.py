import json

print("AWS Job Watcher")
print("-" *20)

with open("config/companies.json", "r") as file:
    companies = json.load(file)

print(companies)

for company in companies:
    print()
    print(f"Checking {company['company']}")
    print (company['url'])