import re
from datetime import datetime
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)

class ScanXAdvancedEngine:
    def analyze_stylometry(self, text_list):
        if not text_list or len(text_list) == 0:
            return {"ai_probability": 0, "verdict": "No Data"}
        total_words = 0
        sentence_lengths = []
        special_char_count = 0
        for text in text_list:
            sentences = sent_tokenize(text)
            words = word_tokenize(text)
            total_words += len(words)
            if len(sentences) > 0:
                sentence_lengths.append(len(words) / len(sentences))
            special_char_count += len(re.findall(r"[!@#$%^&*()_+={}\[\]|\\:]", text))
        avg_sentence_length = (np.mean(sentence_lengths) if sentence_lengths else 0)
        length_variance = np.var(sentence_lengths) if sentence_lengths else 100
        ai_score = 0
        if 12 <= avg_sentence_length <= 25: ai_score += 35
        if length_variance < 15: ai_score += 45
        if (special_char_count / (total_words if total_words > 0 else 1) > 0.15): ai_score += 20
        return {"ai_probability": min(ai_score, 100), "verdict": "AI Generated" if ai_score >= 70 else "Human Written"}

    def analyze_server_heartbeat(self, timestamp_strings):
        if len(timestamp_strings) < 5:
            return {"bot_probability": 0, "verdict": "Insufficient data"}
        timestamps = []
        for ts in timestamp_strings:
            try: timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
            except ValueError: continue
        timestamps.sort()
        time_deltas = [(timestamps[i+1] - timestamps[i]).total_seconds() for i in range(len(timestamps)-1)]
        if not time_deltas: return {"bot_probability": 0, "verdict": "No valid intervals"}
        np_deltas = np.array(time_deltas)
        delta_variance = np.var(np_deltas)
        avg_delta = np.mean(np_deltas)
        mad = np.median(np.abs(np_deltas - np.median(np_deltas)))
        bot_probability = 0
        if delta_variance < 2.0 and avg_delta > 0: bot_probability += 60
        elif delta_variance < 15.0: bot_probability += 40
        if mad < 5.0 and avg_delta > 0: bot_probability += 40
        elif mad < 12.0: bot_probability += 20
        bot_probability = min(bot_probability, 100)
        verdict = "🚨 Bot Detected" if bot_probability >= 80 else "⚠️ Suspicious" if bot_probability >= 50 else "Normal Human"
        return {"bot_probability": bot_probability, "verdict": verdict}

    def cross_platform_persona_tracker(self, username, post_text):
        crypto_links = re.findall(r"(t\.me|telegram|discord|crypto|whatsapp)", post_text.lower())
        suspicious_score = 0
        if len(crypto_links) > 0: suspicious_score += 50
        if re.search(r"\d{5,}", username): suspicious_score += 40
        return {"coordinated_risk_score": suspicious_score, "verdict": "CIB Flagged" if suspicious_score >= 50 else "Safe"}
