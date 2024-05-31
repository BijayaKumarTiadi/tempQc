
import os
import tempfile
import shutil
from django.conf import settings
from itertools import cycle

import google.generativeai as genai
"""
To evenly distribute API requests among multiple API keys
"""
API_KEYS = settings.API_KEYS
api_key_cycle = cycle(API_KEYS)


#Traditional way to configure
# GOOGLE_API_KEY="AIzaSyAvBMy97aMQcbkHKSTk-4jW_NOgPtFvzz0"
# genai.configure(api_key=GOOGLE_API_KEY)

def pdf_processing(pdf_file):
    """
    Processes a PDF file to extract its text content.

    Args:
        pdf_file (File): A file-like object representing the PDF file.

    Returns:
        str: Extracted text content from the PDF file.

    Raises:
        RuntimeError: If any error occurs during the PDF processing.
    """
    temp_file_path = None
    new_temp_file_path = None
    text_file_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(pdf_file.read())
            temp_file_path = temp_file.name

        new_temp_file_path = os.path.join(tempfile.gettempdir(), "pdf_file_temp.pdf")
        shutil.move(temp_file_path, new_temp_file_path)
        
        if os.system(f'pdftotext -layout {new_temp_file_path}') != 0:
            raise RuntimeError("Failed to convert PDF to text")

        text_file_path = new_temp_file_path[:-3] + "txt"
        with open(text_file_path, encoding="utf-8") as f:
            extracted_text = f.read()

        return extracted_text

    except Exception as e:
        raise RuntimeError(f"An error occurred during PDF processing: {str(e)}")

    finally:
        # Cleanup temporary files
        try:
            if text_file_path and os.path.exists(text_file_path):
                os.remove(text_file_path)
            if new_temp_file_path and os.path.exists(new_temp_file_path):
                os.remove(new_temp_file_path)
        except Exception as cleanup_error:
            raise RuntimeError(f"An error occurred during cleanup: {str(cleanup_error)}")
        
        

def gemini_1(pdf_text, response_format):
    """
    Generates a response based on the provided PDF text and response format using the Gemini-1.0-pro model.

    This function requires the `google-generativeai` package. Install it using:
    $ pip install google-generativeai

    Args:
        pdf_text (str): The text extracted from the PDF.
        response_format (dict): The desired response format in JSON.

    Returns:
        str: The generated response text from the Gemini model.

    Raises:
        ValueError: If the input pdf_text or response_format is invalid.
        RuntimeError: If there is an issue with the model generation.
    """
    if not isinstance(pdf_text, str):
        raise ValueError("Invalid input: pdf_text must be a string")
    if not isinstance(response_format, dict):
        raise ValueError("Invalid input: response_format must be a dictionary")
    refined_text = refine_text(response_format, pdf_text)
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        #next api from the setting 
        # api_key = next(api_key_cycle)
        # print("Using API KEY : " + api_key)
        genai.configure(api_key=next(api_key_cycle))


        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to initialize the generative model: {str(e)}")

    try:
        convo = model.start_chat(history=[])
        # response_format = {"desired_key": "desired_value"} # prefer if any json format not recieved.
        convo.send_message(f"{refined_text} AND RESPONSE IN FOLLOWING FORMAT IN JSON {response_format}")
        return convo.last.text
    except Exception as e:
        raise RuntimeError(f"Failed to generate response: {str(e)}")
    
def refine_text(format: dict, text: str) -> str:
    """
    Refines the text by trimming it after specific keywords based on the given format.

    Args:
        format (dict): The format dictionary containing the company name.
        text (str): The text to be refined.

    Returns:
        str: Refined text or the original text if no specific format is found.

    Raises:
        ValueError: If the text or format is invalid.
    """
    if not isinstance(format, dict):
        raise ValueError("Invalid input: format must be a dictionary")
    if not isinstance(text, str):
        raise ValueError("Invalid input: text must be a string")

    company_name = format.get('company_name', '').upper()
    trim_point = None

    if company_name == "SUN PHARMACEUTICAL":
        trim_point = "Subject to Special Terms and Conditions"
    elif company_name == "UNIQUE PHARMACEUTICAL LABS.":
        trim_point = "terms and conditions"
    elif company_name == "PAR FORMULATIONS PRIVATE LIMITED":
        trim_point = "PURCHASE ORDER TERMS AND CONDITIONS"
    elif company_name == "MJ BIOPHARM PVT LTD":
        trim_point = "TERMS AND CONDITIONS"
    elif company_name == "JMEDLEY PHARMACEUTICALS LIMITED":
        trim_point = "Terms & Conditions"
    elif company_name == "Inventia Healthcare Limited":
        trim_point = "TERMS AND CONDITIONS"
    elif company_name == "Glenmark Pharmaceuticals Limited":
        trim_point = "PURCHASE ORDER TERMS AND CONDITIONS"

    if trim_point:
        trim_index = text.lower().find(trim_point.lower())
        if trim_index != -1:
            return text[:trim_index]

    return text


# Thease lines to be removed , meant for testing only .
# pdf_path="B:\\Upwork\\webApp\\WebAppProj\\testing_pdfs\\JB.PDF"
# format = {'company_name': 'MERCK SPECIALITIES PRIVATE LIMITED', 'po_number': 'PO No. :', 'po_date': 'Date:', 'vendor_name': '', 'vendor_address': '', 'vendor_gst_number': '', 'vendor_pan_number': '', 'buyer_name': '', 'buyer_address': '', 'buyer_gst_number': '', 'buyer_pan_number': '', 'items': [{'item_code': 'Material Code', 'description': 'Description', 'quantity': 'Quantity', 'unit_price': 'Rate', 'amount': 'Value', 'DEL_DATE': 'Delivery Date'}, {'item_code': 'Material Code', 'description': 'Description', 'quantity': 'Quantity', 'unit_price': 'Rate', 'amount': 'Value', 'DEL_DATE': 'Delivery Date'}], 'total_amount': 'Total value all inclusive', 'delivery_address': '', 'delivery_date': ''}
# pdf_path="B:\\Upwork\\aipo_rest\\Test Pdfs\\MERCK.PDF"
# with open(pdf_path,"rb") as pdf_file:
#     text = pdf_processing(pdf_file)
#     # print(text)
#     # format = "JB PHARMACEUTICAL"
#     refined_text = refine_text(format, text)
#     print(refined_text)
#     print(len(text))
#     print(len(refined_text))
