import wikipedia

def get_landmark_info(landmark):
    try:
        summary = wikipedia.summary(landmark, sentences=3)
        return summary
    except Exception as e:
        return f"No info found: {e}"
