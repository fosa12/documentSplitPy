import fitz  # PyMuPDF
import json
import os
from docx2pdf import convert
import tempfile
import shutil

# Ścieżka do folderu z plikami PDF i DOCX
input_folder = r"C:\Users\Piotr\Desktop\python"

# Ścieżka do folderu wyjściowego dla plików JSON
output_folder = r"C:\Users\Piotr\Desktop\python_json"

# Utworzenie folderu wyjściowego, jeśli nie istnieje
os.makedirs(output_folder, exist_ok=True)

# Funkcja do konwersji DOCX na PDF
def docx_to_pdf(docx_path, pdf_path):
    try:
        convert(docx_path, pdf_path)
        print(f"Skonwertowano {docx_path} na {pdf_path}.")
        return True
    except Exception as e:
        print(f"Nie udało się skonwertować {docx_path} na PDF. Błąd: {e}")
        return False

# Iteracja przez wszystkie pliki w folderze
for filename in os.listdir(input_folder):
    file_lower = filename.lower()
    file_path = os.path.join(input_folder, filename)

    if file_lower.endswith('.pdf'):
        pdf_path = file_path
    elif file_lower.endswith('.docx'):
        # Utwórz tymczasowy plik PDF w folderze wyjściowym
        pdf_filename = os.path.splitext(filename)[0] + '.pdf'
        pdf_path = os.path.join(input_folder, pdf_filename)

        # Konwertuj DOCX na PDF
        if not docx_to_pdf(file_path, pdf_path):
            continue  # Przejdź do następnego pliku, jeśli konwersja się nie powiodła
    else:
        # Pomijanie plików o innych rozszerzeniach
        continue

    # Teraz, pdf_path zawiera ścieżkę do pliku PDF, który możemy przetworzyć
    if not os.path.isfile(pdf_path):
        print(f"Plik {pdf_path} nie został znaleziony.")
        continue

    # Definiowanie ścieżki do pliku JSON
    json_filename = os.path.splitext(os.path.basename(pdf_path))[0] + '.json'
    json_path = os.path.join(output_folder, json_filename)

    try:
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

        print(f"Dane z {pdf_path} zostały zapisane w pliku {json_path}.")

    except Exception as e:
        print(f"Nie udało się przetworzyć pliku {pdf_path}. Błąd: {e}")

    finally:
        # Jeśli plik PDF był wynikiem konwersji DOCX, usuń tymczasowy PDF
        if file_lower.endswith('.docx') and os.path.isfile(pdf_path):
            try:
                os.remove(pdf_path)
                print(f"Usunięto tymczasowy plik PDF: {pdf_path}.")
            except Exception as e:
                print(f"Nie udało się usunąć tymczasowego pliku {pdf_path}. Błąd: {e}")
