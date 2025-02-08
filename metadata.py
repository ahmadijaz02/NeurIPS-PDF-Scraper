import requests
from bs4 import BeautifulSoup
import csv
import json
import os

BASE_URL = "https://papers.nips.cc"
START_YEAR = 2017
END_YEAR = 2023

# Data storage
papers_data = []

# Create downloads directory if not exists
if not os.path.exists("downloads"):
    os.mkdir("downloads")

# Iterate over each year
for year in range(START_YEAR, END_YEAR + 1):
    year_url = f"{BASE_URL}/paper_files/paper/{year}"
    print(f"Scraping {year_url}...")

    try:
        response = requests.get(year_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract paper links
        for link in soup.select("a[href]"):
            href = link.get("href")
            if "Abstract.html" in href:
                title = link.text.strip()
                abstract_url = BASE_URL + href

                # Extract PDF link
                pdf_url = abstract_url.replace("Abstract.html", "paper.pdf")

                # Store metadata
                papers_data.append({
                    "year": year,
                    "title": title,
                    "abstract_url": abstract_url,
                    "pdf_url": pdf_url
                })

    except Exception as e:
        print(f"Error scraping {year_url}: {e}")

# Save data as CSV
csv_file = "output.csv"
with open(csv_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["year", "title", "abstract_url", "pdf_url"])
    writer.writeheader()
    writer.writerows(papers_data)

print(f"Saved extracted metadata to {csv_file}")

# Save data as JSON
json_file = "output.json"
with open(json_file, "w", encoding="utf-8") as file:
    json.dump(papers_data, file, indent=4)

print(f"Saved extracted metadata to {json_file}")
