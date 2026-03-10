import easyocr

reader = easyocr.Reader(['en'])

def extract_text_from_image(image_path):
    """
    Returns (text, confidence) tuple.
    confidence is the mean confidence across all detected text boxes (0.0 – 1.0).
    """
    result = reader.readtext(image_path)

    if not result:
        return "", 0.0

    text = ""
    total_conf = 0.0

    for detection in result:
        # detection = (bbox, text, confidence)
        text       += detection[1] + " "
        total_conf += detection[2]

    mean_conf = total_conf / len(result)
    return text.strip(), round(mean_conf, 3)