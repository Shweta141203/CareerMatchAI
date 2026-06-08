from PyPDF2 import PdfReader
reader= PdfReader("sampleResume.pdf")

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text() 
            if page_text: # Check if text extraction was successful for the page
                text += page_text

        return text.strip()

    except Exception as e:
        print("Error while extracting PDF:", e)
        return None

"""reader= PdfReader("sampleResume.pdf")

print(len(reader.pages))

first_page = reader.pages[1]
print(first_page.extract_text())

text = ""
for page in reader.pages:
    text += page.extract_text()

print("Total characters:", len(text))
print("Total words:", len(text.split()))"""

import re

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

