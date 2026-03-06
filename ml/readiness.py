def predict_readiness(hours, completion, confidence):
    score = (hours * 0.4) + (completion * 0.35) + (confidence * 0.25)
    return min(100, round(score, 2))