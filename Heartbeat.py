import re
from datetime import datetime
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize

# NLTK के मुफ़्त रिसोर्स को पहली बार चलाने पर ऑटो-डाउनलोड करना
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)


class ScanXAdvancedEngine:

    def _init_(self):
        print("🚀 Scan X Advanced Forensic Engine Activated...")

    # =========================================================================
    # 🔥 FEATURE 1: Generative AI "Stylometry" Engine (AI Language Detection)
    # =========================================================================
    def analyze_stylometry(self, text_list):
        """Analyzes text structure to catch robotic patterns typical of ChatGPT/LLMs."""
        if not text_list or len(text_list) == 0:
            return {"ai_probability": 0, "status": "No Data", "verdict": "No Data"}

        total_words = 0
        total_sentences = 0
        sentence_lengths = []
        special_char_count = 0

        for text in text_list:
            sentences = sent_tokenize(text)
            words = word_tokenize(text)

            total_sentences += len(sentences)
            total_words += len(words)

            if len(sentences) > 0:
                sentence_lengths.append(len(words) / len(sentences))

            # Count robotic or spammy repetitive special characters
            special_char_count += len(re.findall(r"[!@#$%^&*()_+={}\[\]|\\:]", text))

        avg_sentence_length = (
            np.mean(sentence_lengths) if sentence_lengths else 0
        )
        length_variance = np.var(sentence_lengths) if sentence_lengths else 100

        ai_score = 0
        if 12 <= avg_sentence_length <= 25:  # AI's sweet spot
            ai_score += 35
        if length_variance < 15:  # Bot uniformity
            ai_score += 45
        if (
            special_char_count / (total_words if total_words > 0 else 1) > 0.15
        ):  # High spam symbol density
            ai_score += 20

        return {
            "ai_probability": min(ai_score, 100),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "text_uniformity_variance": round(length_variance, 2),
            "verdict": "AI Generated" if ai_score >= 70 else "Human Written",
        }

    # =========================================================================
    # ⏱️ FEATURE 2 (OPTIMIZED): Server Heartbeat Anomaly (Variance + MAD Logic)
    # =========================================================================
    def analyze_server_heartbeat(self, timestamp_strings):
        """Calculates Variance AND Median Absolute Deviation (MAD) with optimized numpy speed."""
        if len(timestamp_strings) < 5:
            return {
                "heartbeat_detected": False,
                "bot_probability": 0,
                "reason": "Insufficient data",
                "verdict": "Insufficient data",
                "flags_triggered": []
            }

        timestamps = []
        for ts in timestamp_strings:
            try:
                timestamps.append(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S"))
            except ValueError:
                continue

        timestamps.sort()

        time_deltas = []
        for i in range(len(timestamps) - 1):
            delta = (timestamps[i + 1] - timestamps[i]).total_seconds()
            time_deltas.append(delta)

        if not time_deltas:
            return {
                "heartbeat_detected": False, 
                "bot_probability": 0, 
                "reason": "No valid intervals",
                "verdict": "No valid intervals",
                "flags_triggered": []
            }

        # Convert to numpy array for enterprise performance speed
        np_deltas = np.array(time_deltas)
        delta_variance = np.var(np_deltas)
        avg_delta = np.mean(np_deltas)

        # High-performance MAD calculation using numpy directly
        median_delta = np.median(np_deltas)
        mad = np.median(np_abs(np_deltas - median_delta))

        bot_probability = 0
        reasons = []

        if delta_variance < 2.0 and avg_delta > 0:
            bot_probability += 60
            reasons.append("Ultra-low time variance detected (Static Interval)")
        elif delta_variance < 15.0:
            bot_probability += 40
            reasons.append("Low time variance detected (Scheduled Script)")

        if mad < 5.0 and avg_delta > 0:
            bot_probability += 40
            reasons.append("High pattern consistency caught by MAD (Smart/Jitter Bot)")
        elif mad < 12.0:
            bot_probability += 20
            reasons.append("Moderate pattern consistency caught by MAD")

        bot_probability = min(bot_probability, 100)

        if bot_probability >= 80:
            verdict = "🚨 100% Automated Script/Server Detected"
        elif bot_probability >= 50:
            verdict = "⚠️ High Probability of Scheduled/Smart Bot"
        else:
            verdict = "Normal Human Timing (Organic)"

        return {
            "heartbeat_detected": True if bot_probability >= 50 else False,
            "time_delta_variance_seconds": round(delta_variance, 4),
            "median_gap_seconds": round(median_delta, 2),
            "median_absolute_deviation_mad": round(mad, 4),
            "avg_gap_seconds": round(avg_delta, 2),
            "bot_probability": bot_probability,
            "flags_triggered": reasons,  # Returns clean empty list if no flags
            "verdict": verdict,
        }

    # =========================================================================
    # 🌐 FEATURE 3: Cross-Platform Coordinated Persona Tracking
    # =========================================================================
    def cross_platform_persona_tracker(self, username, post_text):
        """Flags footprints pointing to multi-platform coordinated bot network grids."""
        crypto_links = re.findall(
            r"(t\.me|telegram|discord|crypto|whatsapp)", post_text.lower()
        )

        platforms_found = []
        suspicious_score = 0

        if len(crypto_links) > 0:
            platforms_found.append("Telegram / Discord Channels")
            suspicious_score += 50

        if re.search(r"\d{5,}", username):
            platforms_found.append("Coordinated Multi-Platform Name Grid")
            suspicious_score += 40

        return {
            "cross_platform_spam": True if suspicious_score >= 50 else False,
            "detected_networks": platforms_found if platforms_found else ["None Isolated"],
            "coordinated_risk_score": suspicious_score,
            "verdict": "Coordinated Inauthentic Behavior (CIB) Flagged" if suspicious_score >= 50 else "Safe",
        }


  if _name_ == "_main_"
    engine = ScanXAdvancedEngine()

    print("\n--- 1. Testing AI Stylometry Engine ---")
    ai_tweets = [
        "Cryptocurrency markets exhibit significant volatility today. Ensure proper risk mitigation strategies.",
        "To optimize your portfolio, click the link to join our exclusive network. Financial growth awaits.",
    ]
    print(engine.analyze_stylometry(ai_tweets))

    print("\n--- 2. Testing Server Heartbeat Anomaly (Advanced Jitter Test) ---")
    smart_bot_timestamps = [
        "2026-06-28 10:00:00",
        "2026-06-28 10:05:01",
        "2026-06-28 10:10:00",
        "2026-06-28 10:25:00",
        "2026-06-28 10:30:02",
    ]
    print(engine.analyze_server_heartbeat(smart_bot_timestamps))
