import re

def clean_text(text):
    """
    Remove HTML tags and extra spaces
    """
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def summarize_text(text, max_sentences=2):
    """
    Improved extractive summarization.
    Produces clean, readable sentences.
    """
    if not text:
        return ""

    text = clean_text(text)

    # Split text into sentences properly
    sentences = re.split(r'(?<=[.!?])\s+', text)

    # Filter meaningful sentences
    clean_sentences = []
    for s in sentences:
        s = s.strip()
        if len(s.split()) >= 5:
            s = s[0].upper() + s[1:] if len(s) > 1 else s
            clean_sentences.append(s)

    # Select top sentences
    summary = ". ".join(clean_sentences[:max_sentences])

    # Ensure proper ending punctuation
    if summary and not summary.endswith("."):
        summary += "."

    return summary
