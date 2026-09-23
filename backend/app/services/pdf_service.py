from pdf2image import convert_from_path
from app.services.ocr_service import extract_text_from_image


def extract_text_from_pdf(file_path: str) -> list[str]:
    #convert multi page pdf into list of PIL(pillow) image objects.
    pages = convert_from_path(file_path)

    all_text = []

    for index, page in enumerate(pages):
        image_path = f"uploads/temp_page_{index + 1}.png"
        page.save(image_path)

        page_text = extract_text_from_image(image_path)
        all_text.extend(page_text)

    return all_text