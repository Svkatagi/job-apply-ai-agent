# src/tools/token_counter.py

def count_tokens(text: str) -> int:
    """
    Roughly estimate the number of tokens in a text.
    
    Assumption:
    - 1 token ≈ 4 characters (average for English language).
    
    Args:
        text (str): The input text.

    Returns:
        int: Estimated number of tokens.
    """
    if not text:
        return 1  # Always return at least 1 token even if text is empty

    return max(1, len(text) // 4)
