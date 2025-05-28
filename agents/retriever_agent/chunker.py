from nltk.tokenize import sent_tokenize

# Optional: Download punkt tokenizer if not already
try:
    sent_tokenize("Test")
except LookupError:
    import nltk
    nltk.download('punkt')

def chunk_text(text: str, max_tokens: int = 100) -> list:
    """
    Splits long text into chunks based on sentence boundaries, 
    each with approximately max_tokens worth of content.
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_length = 0
        current_chunk.append(sentence)
        current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

