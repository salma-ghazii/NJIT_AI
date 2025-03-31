# import requests
# from bs4 import BeautifulSoup
# from fpdf import FPDF

# # URL to scrape
# url = "https://cs.njit.edu/"

# # Fetch the HTML content of the page
# response = requests.get(url)
# if response.status_code == 200:
#     html_content = response.text
#     # Parse the HTML using BeautifulSoup
#     soup = BeautifulSoup(html_content, 'html.parser')
    
#     # Extract text content from the page
#     text_content = soup.get_text(separator="\n", strip=True)
    
#     # Create a PDF object
#     pdf = FPDF()
#     pdf.set_auto_page_break(auto=True, margin=15)
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)

#     # Split text into lines to prevent PDF overflow
#     for line in text_content.split("\n"):
#         pdf.cell(200, 10, txt=line, ln=True)

#     # Save the scraped data to a PDF file
#     pdf_filename = "njit_cs_data.pdf"
#     pdf.output(pdf_filename)

#     print(f"NJIT CS data saved to {pdf_filename}")
# else:
#     print(f"Failed to fetch the page. Status code: {response.status_code}")


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Set to avoid re-scraping the same page
visited_urls = set()

def scrape_page(url, base_url):
    """Scrapes a page, extracts text, finds sub-links, and returns text + sub-links."""
    if url in visited_urls:
        return "", []  # Skip already visited pages

    visited_urls.add(url)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return "", []

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract page text
        text_content = soup.get_text(separator="\n", strip=True)

        # Extract all subpage links (only within the same domain)
        sub_links = set()
        for link in soup.find_all("a", href=True):
            full_url = urljoin(base_url, link["href"])
            if urlparse(full_url).netloc == urlparse(base_url).netloc:  # Same domain check
                sub_links.add(full_url)

        return text_content, sub_links

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return "", []

def scrape_website(start_url, max_pages=10):
    """Recursively scrapes a website and collects text into a single document."""
    base_url = start_url
    pages_to_scrape = {start_url}
    all_text = ""
    # visited_urls = set()

    while pages_to_scrape and len(visited_urls) < max_pages:
        current_page = pages_to_scrape.pop()
        print(f"Scraping: {current_page}")

        page_text, sub_links = scrape_page(current_page, base_url)
        all_text += f"\n\n---\n\nPage: {current_page}\n\n{page_text}"

        # Add new sub-links to scrape
        # print(type(sub_links))
        # print(type(visited_urls))
        pages_to_scrape.update(set(sub_links) - visited_urls)

    return all_text

def save_to_pdf(text, filename="scraped_data.pdf"):
    """Saves text into a properly formatted PDF using reportlab."""
    pdf = canvas.Canvas(filename, pagesize=letter)
    pdf.setFont("Helvetica", 10)

    # Set margins and initial position
    x_margin, y_margin = 50, 750  
    line_height = 12  # Line spacing

    y_position = y_margin

    # Add text to the PDF
    for line in text.split("\n"):
        if y_position < 50:  # Check if page is full, add a new page
            pdf.showPage()
            pdf.setFont("Helvetica", 10)
            y_position = y_margin

        pdf.drawString(x_margin, y_position, line[:1000])  # Limit to 1000 chars per line
        y_position -= line_height

    pdf.save()
    print(f"Data saved to {filename}")

# Set your starting URL (e.g., NJIT CS website)
start_url = "https://cs.njit.edu/"

# Scrape website and generate PDF
# scraped_text = scrape_website(start_url, max_pages=50)
# save_to_pdf(scraped_text, "njit_cs_full_data.pdf")

start_url = "https://www.njit.edu/"
scraped_text = scrape_website(start_url, max_pages=50)
save_to_pdf(scraped_text, "njit_general_full_data.pdf")



