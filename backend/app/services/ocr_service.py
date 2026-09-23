from paddleocr import PaddleOCR


ocr = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
    enable_mkldnn=False,
)

def extract_text_from_image(image_path : str) -> list[str]:
    result = ocr.predict(image_path)

    if not result:
        return []
    # it retutn all reccognize texts
    return result[0]["rec_texts"]