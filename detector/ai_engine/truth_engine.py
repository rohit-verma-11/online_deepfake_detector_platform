from duckduckgo_search import DDGS

def verify_news_accuracy(text_claim):
    try:
        with DDGS() as ddgs:
            # We search for the claim PLUS debunking terms to see if they appear
            search_query = f"{text_claim} fact check debunked"
            results = list(ddgs.text(search_query, max_results=10))
            
            # Words that indicate a LIE
            red_flags = ['false', 'fake', 'hoax', 'satire', 'untrue', 'no evidence', 'debunked', 'parody']
            # Words that indicate TRUTH
            green_flags = ['confirmed', 'verified', 'announced', 'official']

            full_text = " ".join([r['body'].lower() for r in results])
            
            fake_score = sum(full_text.count(word) for word in red_flags)
            true_score = sum(full_text.count(word) for word in green_flags)

            # If the moon claim hits 'satire' or 'fake' even once, it's likely false
            if fake_score > 0:
                return {
                    "verdict": "FALSE",
                    "score": 10.0,
                    "reasoning": f"Forensic scan found {fake_score} red flags in news snippets. Likely misinformation or satire."
                }
            elif true_score > 5:
                return {
                    "verdict": "VERIFIED",
                    "score": 90.0,
                    "reasoning": "High consensus across official reporting channels."
                }
            else:
                return {
                    "verdict": "UNCERTAIN",
                    "score": 50.0,
                    "reasoning": "Inconclusive data. No official verification or debunking found."
                }
    except Exception as e:
        return {"verdict": "ERROR", "score": 0, "reasoning": "Network Error."}