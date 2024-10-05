import fitz  # PyMuPDF
import json
import os

# Ścieżka do pliku PDF
pdf_path = r"C:\Users\Piotr\Desktop\python\dokument1.pdf"

# Ścieżka do pliku wyjściowego JSON
json_path = r"C:\Users\Piotr\Desktop\python\dokument1.json"

# Sprawdzenie, czy plik PDF istnieje
if not os.path.isfile(pdf_path):
    print(f"Plik {pdf_path} nie został znaleziony.")
    exit(1)

# Otwieranie pliku PDF
with fitz.open(pdf_path) as doc:
    data = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Indeksowanie od 0
        text = page.get_text("text")
        data.append({
            "page_number": page_num + 1,  # Numerowanie stron od 1
            "content": text.strip()
        })

# Zapisanie danych do pliku JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Dane zostały zapisane w pliku {json_path}.")


import logging
import fitz  # PyMuPDF
import json
import os
import azure.functions as func
from azure.storage.blob import BlobClient

def main(myblob: func.InputStream):
    logging.info(f"Przetwarzanie pliku: {myblob.name}, rozmiar: {myblob.length} bytes")

    try:
        # Ścieżki plików lokalnych tymczasowych
        temp_pdf_path = f"/tmp/{os.path.basename(myblob.name)}"
        temp_json_path = f"/tmp/{os.path.splitext(os.path.basename(myblob.name))[0]}.json"

        # Zapisz blob do lokalnego pliku tymczasowego
        with open(temp_pdf_path, "wb") as f:
            f.write(myblob.read())

        # Otwórz i przetwórz PDF
        with fitz.open(temp_pdf_path) as doc:
            data = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)  # Indeksowanie od 0
                text = page.get_text("text")
                data.append({
                    "page_number": page_num + 1,  # Numerowanie stron od 1
                    "content": text.strip()
                })

        # Zapisz dane do lokalnego pliku JSON
        with open(temp_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        # Połącz z kontenerem docJson
        # Pobierz zmienną środowiskową na połączenie do Storage
        connect_str = os.getenv('AzureWebJobsStorage')
        if not connect_str:
            logging.error("Brak zmiennej środowiskowej 'AzureWebJobsStorage'.")
            return

        # Utwórz klienta blob dla docJson
        blob_name = f"{os.path.splitext(os.path.basename(myblob.name))[0]}.json"
        output_container = "docjson"  # Upewnij się, że nazwa jest małymi literami

        blob_client = BlobClient.from_connection_string(
            conn_str=connect_str,
            container_name=output_container,
            blob_name=blob_name
        )

        # Otwórz lokalny plik JSON i prześlij go do kontenera docJson
        with open(temp_json_path, "rb") as data_file:
            blob_client.upload_blob(data_file, overwrite=True)
            logging.info(f"Plik JSON zapisany jako {blob_name} w kontenerze {output_container}.")

        # Opcjonalnie: Usuń pliki tymczasowe
        os.remove(temp_pdf_path)
        os.remove(temp_json_path)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")