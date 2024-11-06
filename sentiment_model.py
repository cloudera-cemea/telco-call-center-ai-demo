from typing import Dict, List
import logging

from transformers import pipeline

logging.getLogger().setLevel(logging.INFO)

MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
sentiment_model = pipeline(task="sentiment-analysis", model=MODEL)

def _get_max_score_label(scores: List[Dict]) -> str:
    """
    Given a list of scores, where each score is a dictionary with keys 'label'
    and 'score', the function returns the label with the maximum score.

    Args:
    scores (List[Dict]): List of scores, where each score is a dictionary with
        keys 'label' and 'score'.

    Returns:
    str: The label with the maximum score

    Example:
    get_max_score_label([
        {'label': 'negative', 'score': 0.0042450143955647945},
        {'label': 'neutral', 'score': 0.011172760277986526},
        {'label': 'positive', 'score': 0.984582245349884}
    ])
    Output: 'positive'
    """
    max_score = max(scores, key=lambda x: x['score'])
    return max_score['label']

def predict(data: Dict[str, str]) -> Dict:
    """Run sentiment analysis on a given input text using a pre-trained model.

    Args:
    data (Dict[str, str]): The input data with at least the key "text" and value of
        type string.

    Returns:
    Dict: The original dictionary with all keys and sentiment analysis results.

    Example input:
    {
        "text":"I love hackathons!"
    }

    Example output: 

    {
        'text': 'I love hackathons!',
        'negative': 0.0042450143955647945,
        'neutral': 0.011172760277986526,
        'positive': 0.984582245349884
    }

    Raises:
    TypeError: If data is not a dictionary.
    TypeError: If data does not contain a key of "text".
    TypeError: If data["text"] is not a string.
    """

    logging.info("begin parsing input data")

    if not isinstance(data, dict):
        raise TypeError("data must be a dictionary")
    if "text" not in data:
        raise TypeError("data must contain a key of 'text'")

    text = data["text"]
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    logging.info("end parsing input data without exceptions")

    logging.info("begin model inference")
    try:
        predictions = sentiment_model(text, return_all_scores=True)[0]
    except Exception as e:
        logging.info(f"end model inference with exception: {e}")

    logging.info("end model inference without exception")

    for p in predictions:
        data[p["label"]] = p["score"]

    data["label"] = _get_max_score_label(predictions)

    return data
