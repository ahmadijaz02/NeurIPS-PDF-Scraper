# NeurIPS Paper Scraper  

## Overview  
This project contains web scraping scripts written in Java and Python to extract metadata and download research papers from the NeurIPS (Neural Information Processing Systems) conference website. The extracted data includes paper titles, authors, and PDF download links.  

## Files Included  
- **scraper.java** – Web scraper implemented in Java.  
- **scraper.py** – Web scraper implemented in Python.  
- **output.csv** – Extracted metadata containing paper details.  

## Requirements  

### Python Dependencies:  
Ensure you have Python installed. Install the required libraries using:  
`pip install requests beautifulsoup4 tqdm`  

### Java Dependencies:  
Ensure you have Java installed along with the following:  
- **JSoup** (for HTML parsing)  
- **Apache Commons IO** (for file handling)  

## Running the Scraper  

### Prerequisites  

#### Python (VS Code)  
1. Install Python 3.x.  
2. Install dependencies:  
`pip install requests beautifulsoup4 tqdm`  

#### Java (Eclipse)  
1. Install Java Development Kit (JDK 8 or later).  
2. Download **JSoup** and add it to the Java classpath.  

### Running the Scraper  

#### Python Script (`scraper.py`)  
1. Open a terminal or command prompt.  
2. Navigate to the script directory.  
3. Run the script: `python scraper.py`  
4. The scraped metadata will be saved as `output.csv` and `output.json`.  
5. The downloaded PDFs will be stored in the `downloads` directory, categorized by year.  

#### Java Script (`scraper.java`)  
1. Open Eclipse and ensure **JSoup** is included in the project.  
2. Compile the Java file: `javac -cp .:jsoup-1.13.1.jar scraper.java`  
3. Run the scraper: `java -cp .:jsoup-1.13.1.jar scraper`  
4. Metadata will be saved, and PDFs will be stored in respective year folders.  

## Features  
- Extracts metadata (title, authors, PDF link) for NeurIPS papers.  
- Downloads research papers in parallel using threading.  
- Categorizes papers into year-based folders.  

## Challenges Faced  
- **Rate Limiting** – Added delays to avoid blocking.  
- **JavaScript Rendering** – Used BeautifulSoup (Python) and JSoup (Java) to parse static HTML.  
- **Pagination Handling** – Extracted multiple years with multi-threading.  

## Responsible Web Scraping Practices  
- Follow website `robots.txt` guidelines.  
- Limit request frequency to avoid server overload.  
- Use the scraped data for academic/research purposes only.  

## Blog Post  
Read about the complete scraping process on Medium:  
[https://substack.com/home/post/p-156439442](https://substack.com/home/post/p-156439442)  
