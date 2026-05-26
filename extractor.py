import requests
from bs4 import BeautifulSoup
import PyPDF2



def extract_from_url(url):

    try:
        response = requests.get(url)

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        paragraphs = soup.find_all("p")

        text = " ".join(
            [p.get_text() for p in paragraphs]
        )

        return text

    except:
        return "Error extracting from URL"


# Extract text from uploaded file
def extract_from_file(filepath):

    try:

        # PDF file
        if filepath.endswith(".pdf"):

            text = ""

            with open(filepath, "rb") as f:

                reader = PyPDF2.PdfReader(f)

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text

            return text

        # TXT file
        elif filepath.endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()

        else:
            return "Unsupported file format"

    except:
        return "Error extracting from file"