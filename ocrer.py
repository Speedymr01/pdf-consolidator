import os
import logging
from datetime import datetime
import fitz  # PyMuPDF for text extraction
import time

# Constants
LOG_DIR = 'logs'
PROCESSED_FILES_PATH_OCR = 'processed_ocr.txt'
SLEEP_INTERVAL = 10  # seconds
INPUT_DIR = './pdfs'
OUTPUT_DIR = './output'

# Configure logging with dynamic filename
log_filename = os.path.join(LOG_DIR, f'ocr_processing_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
os.makedirs(os.path.dirname(log_filename), exist_ok=True)
logging.basicConfig(filename=log_filename, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_processed_files(processed_files_path):
    """Load the set of processed files from the processed.txt file."""
    if os.path.exists(processed_files_path):
        with open(processed_files_path, 'r') as file:
            return set(file.read().splitlines())
    return set()

def save_processed_file(filename, processed_files_path):
    """Save a processed file name to the processed.txt file."""
    with open(processed_files_path, 'a') as file:
        file.write(filename + '\n')

def ocr_pdf(pdf_path, output_path):
    """
    ...existing code...
    """
    try:
        # Open the PDF
        pdf_document = fitz.open(pdf_path)
        text = ""

        # Extract text from each page
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            text += page.get_text() + "\n"

        # Save the extracted text to a file
        output_txt_file = output_path + ".txt"
        with open(output_txt_file, "w", encoding="utf-8") as f:
            f.write(text)
        logging.info(f"OCR completed for {pdf_path}. Output saved to {output_txt_file}")

    except (fitz.FileDataError, fitz.FileNotFoundError, fitz.PdfError) as e:
        logging.error(f"Error during OCR for {pdf_path}: {e}")

def process_pdf(input_pdf, output_dir, processed_files_path):
    """
    ...existing code...
    """
    try:
        # Extract the filename from the input path
        input_file_name = os.path.splitext(os.path.basename(input_pdf))[0]

        ocr_output_base = input_file_name  # Remove .pdf extension
        output_txt_path = os.path.join(output_dir, ocr_output_base)  # Output path for OCR'd text

        ocr_pdf(input_pdf, output_txt_path)
        logging.info(f"OCR completed for {input_pdf}. Output saved to {output_dir}")

    except Exception as e:
        logging.error(f"Error processing PDF {input_pdf}: {e}")

def monitor_directory(input_dir):
    """Monitor the input directory for new PDF files and process them if they haven't been processed."""
    processed_files = load_processed_files(PROCESSED_FILES_PATH_OCR)

    while True:
        try:
            new_files_found = False
            for item in os.listdir(input_dir):
                item_path = os.path.join(input_dir, item)

                if os.path.isfile(item_path) and item.endswith(".pdf"):
                    if item in processed_files:
                        print(f"File {item} already processed.")
                        logging.info(f"File {item} already processed.")
                    else:
                        # Handle single PDF file
                        new_files_found = True
                        output_dir = os.path.join(OUTPUT_DIR, f"OCR - {os.path.splitext(item)[0]}")
                        os.makedirs(output_dir, exist_ok=True)
                        logging.info(f"New file detected: {item_path}")
                        process_pdf(item_path, output_dir, PROCESSED_FILES_PATH_OCR)
                        processed_files.add(item)
                        save_processed_file(item, PROCESSED_FILES_PATH_OCR)
                        print(f"Processed {item}")
                        logging.info(f"Processed {item}")

                elif os.path.isdir(item_path):
                    # Handle directory of PDF files
                    for filename in os.listdir(item_path):
                        if filename.endswith(".pdf"):
                            pdf_path = os.path.join(item_path, filename)
                            if filename in processed_files:
                                print(f"File {filename} in {item} already processed.")
                                logging.info(f"File {filename} in {item} already processed.")
                            else:
                                new_files_found = True
                                output_dir = os.path.join(OUTPUT_DIR, f"OCR - {item}")
                                os.makedirs(output_dir, exist_ok=True)
                                logging.info(f"New file detected: {pdf_path}")
                                process_pdf(pdf_path, output_dir, PROCESSED_FILES_PATH_OCR)
                                processed_files.add(filename)
                                save_processed_file(filename, PROCESSED_FILES_PATH_OCR)
                                print(f"Processed {filename} in {item}")
                                logging.info(f"Processed {filename} in {item}")
            
            if not new_files_found:
                print("No new files found.")
                logging.info("No new files found.")
        except Exception as e:
            logging.error(f"Error monitoring directory {input_dir}: {e}")

        time.sleep(SLEEP_INTERVAL)  # Check for new files every SLEEP_INTERVAL seconds

if __name__ == "__main__":
    logging.info(f"Input directory: {INPUT_DIR}")
    logging.info(f"Output directory: {OUTPUT_DIR}")

    monitor_directory(INPUT_DIR)