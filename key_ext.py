import spacy
import nltk
from nltk.corpus import wordnet as wn
nltk.download('wordnet', quiet=True)

# ✅ Load the best available spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Using 'en_core_web_sm' instead.")
    nlp = spacy.load("en_core_web_sm")


def extract_smart_keyword(sentence: str) -> str:
    """
    Extract the most contextually relevant keyword from any sentence.
    Automatically adapts to topic and avoids irrelevant terms.
    """
    if not sentence or len(sentence.strip()) < 2:
        return ""

    doc = nlp(sentence)

    # Gather candidate nouns and noun phrases
    candidates = []
    for chunk in doc.noun_chunks:
        # Skip pronouns or trivial words
        if chunk.root.pos_ in ["PRON"] or chunk.root.text.lower() in ["it", "this", "that", "something"]:
            continue
        candidates.append(chunk.text)

    if not candidates:
        # fallback: use any noun or proper noun
        candidates = [t.text for t in doc if t.pos_ in ("NOUN", "PROPN") and not t.is_stop]

    if not candidates:
        return sentence.strip()

    # Compute context vector (mean of all token vectors)
    context_tokens = [t.vector for t in doc if t.has_vector and not t.is_stop]
    if not context_tokens:
        return candidates[0].capitalize()
    import numpy as np
    context_vector = np.mean(context_tokens, axis=0)

    # Compute similarity score for each candidate
    best_word, best_score = None, -1
    for cand in candidates:
        token_doc = nlp(cand)
        if token_doc.vector_norm == 0:
            continue
        sim = token_doc.similarity(doc)
        if sim > best_score:
            best_score, best_word = sim, cand

    # Optional: generalize meaning via WordNet
    if best_word:
        synsets = wn.synsets(best_word)
        if synsets:
            hypernyms = synsets[0].hypernyms()
            if hypernyms:
                best_word = hypernyms[0].lemmas()[0].name().replace("_", " ")

    return best_word.capitalize() if best_word else sentence.strip()
