import os
import requests
import csv
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

BASE_URL = "https://papers.nips.cc"
START_YEAR = 2017
END_YEAR = 2023
MAIN_THREAD_POOL_SIZE = 10  # Parallel year downloads
YEAR_THREAD_POOL_SIZE = 20  # Parallel paper downloads per year

# Directories
main_download_dir = "downloads"
os.makedirs(main_download_dir, exist_ok=True)

# Output files
CSV_FILE = "output.csv"
JSON_FILE = "output.json"

def get_paper_metadata(year):
    """Fetches paper metadata for a given year."""
    year_url = f"{BASE_URL}/paper_files/paper/{year}"
    print(f"Fetching metadata for {year}: {year_url}")

    try:
        response = requests.get(year_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        papers = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if (year <= 2020 and "Abstract.html" in href) or (year > 2020 and "/hash/" in href):
                title = link.text.strip()
                abstract_url = BASE_URL + href
                pdf_url = abstract_url.replace("Abstract.html", "paper.pdf") if "Abstract.html" in href else abstract_url + ".pdf"
                papers.append({"year": year, "title": title, "abstract_url": abstract_url, "pdf_url": pdf_url})

        return papers
    except requests.RequestException as e:
        print(f"Error fetching metadata for {year}: {e}")
        return []

def save_metadata(metadata):
    """Saves metadata to CSV and JSON files."""
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["year", "title", "abstract_url", "pdf_url"])
        writer.writeheader()
        writer.writerows(metadata)

    with open(JSON_FILE, "w", encoding="utf-8") as jsonfile:
        json.dump(metadata, jsonfile, indent=4)

    print(f"Metadata saved to {CSV_FILE} and {JSON_FILE}")

def download_paper(paper, download_dir):
    """Downloads a paper's PDF and saves it with its title."""
    pdf_url = paper["pdf_url"]
    title = paper["title"]
    title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title)  # Sanitize filename
    pdf_filename = f"{title}.pdf"
    pdf_path = os.path.join(download_dir, pdf_filename)

    if os.path.exists(pdf_path):
        print(f"Already downloaded: {pdf_filename}")
        return

    try:
        pdf_response = requests.get(pdf_url, timeout=15, stream=True)
        pdf_response.raise_for_status()

        with open(pdf_path, "wb") as f:
            for chunk in pdf_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        print(f"Downloaded: {pdf_filename}")
    except requests.RequestException as e:
        print(f"Error downloading {pdf_url}: {e}")

def process_year(year, papers):
    """Downloads papers for a given year using threading."""
    download_dir = os.path.join(main_download_dir, str(year))
    os.makedirs(download_dir, exist_ok=True)

    with ThreadPoolExecutor(max_workers=YEAR_THREAD_POOL_SIZE) as paper_executor:
        list(tqdm(paper_executor.map(lambda paper: download_paper(paper, download_dir), papers), 
                  total=len(papers), desc=f"Year {year}"))

if __name__ == "__main__":
    # Step 1: Extract metadata
    all_papers = []
    with ThreadPoolExecutor(max_workers=MAIN_THREAD_POOL_SIZE) as executor:
        results = list(executor.map(get_paper_metadata, range(START_YEAR, END_YEAR + 1)))
    
    for papers in results:
        all_papers.extend(papers)
    
    save_metadata(all_papers)
    
    # Step 2: Download PDFs
    year_paper_map = {}
    for paper in all_papers:
        year_paper_map.setdefault(paper["year"], []).append(paper)
    
    with ThreadPoolExecutor(max_workers=MAIN_THREAD_POOL_SIZE) as executor:
        executor.map(lambda year: process_year(year, year_paper_map[year]), year_paper_map.keys())
    
    print("All PDFs downloaded.")