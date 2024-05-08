
import os
import tempfile
import shutil

import google.generativeai as genai

GOOGLE_API_KEY="AIzaSyAvBMy97aMQcbkHKSTk-4jW_NOgPtFvzz0"
genai.configure(api_key=GOOGLE_API_KEY)

def pdf_processing(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_file.read())
        temp_file_path = temp_file.name
        temp_file.close()
        new_temp_file_path = os.path.join(tempfile.gettempdir(), "pdf_file_temp.pdf")
        shutil.move(temp_file_path, new_temp_file_path)
        os.system('pdftotext -layout ' + new_temp_file_path)
        text_file_path = new_temp_file_path[:-3] + "txt"
        with open(text_file_path, encoding="utf-8") as f:
            extracted_text = f.read()
        os.remove(text_file_path)
        os.remove(new_temp_file_path)
        return extracted_text


def gemini_1(pdf_text,response_format):
    """
    At the command line, only need to run once to install the package via pip:

    $ pip install google-generativeai
    """
    generation_config = {
    "temperature": 0.9,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)

    convo = model.start_chat(history=[
    ])

    convo.send_message(str(pdf_text) +" AND RESPONSE IN FOLLOWING FORMAT IN JSON   "+ str(response_format))
    return convo.last.text