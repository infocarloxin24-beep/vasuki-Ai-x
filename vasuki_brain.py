# ==========================================
# VASUKI AI 4.0 INTELLIGENCE SYSTEM INTEGRATION
# ==========================================
import math
import re # FIX: re import add kiya
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class VasukiAIIntelligence:
    def _init_(self):
        pass

    def _clean_text(self, text):
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text

    def calculate_semantic_similarity(self, text1, text2):
        clean1 = self._clean_text(text1)
        clean2 = self._clean_text(text2)
        if not clean1.strip() or not clean2.strip():
            return 0.0
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([clean1, clean2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            return round(float(similarity[0][0]) * 100, 2)
        except ValueError:
            return 0.0

    def calculate_fuzzy_distance(self, word1, word2):
        w1, w2 = str(word1).lower(), str(word2).lower()
        if len(w1) < len(w2):
            return self.calculate_fuzzy_distance(w2, w1)
        if len(w2) == 0:
            return len(w1)
        previous_row = range(len(w2) + 1)
        for i, c1 in enumerate(w1):
            current_row = [i + 1]
            for j, c2 in enumerate(w2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1!= c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        distance = previous_row[-1]
        max_len = max(len(w1), len(w2))
        return round((1 - distance / max_len) * 100, 2) if max_len > 0 else 0.0

    def scan_bot_noise_and_entropy(self, text):
        if not text:
            return 0.0
        clean_text = str(text).lower()
        frequencies = {}
        for char in clean_text:
            frequencies[char] = frequencies.get(char, 0) + 1
        entropy = 0
        total_chars = len(clean_text)
        for count in frequencies.values():
            p = count / total_chars
            entropy -= p * math.log2(p)
        special_and_digits = len(re.findall(r'[\d_\W]', str(text)))
        noise_ratio = (special_and_digits / total_chars) * 100 if total_chars > 0 else 0
        bot_score = (entropy * 10) + (noise_ratio * 0.5)
        return round(min(bot_score, 100.0), 2)

    def analyze_text(self, text1, text2):
        semantic_score = self.calculate_semantic_similarity(text1, text2)
        fuzzy_score = self.calculate_fuzzy_distance(text1, text2)
        bot_noise_t1 = self.scan_bot_noise_and_entropy(text1)
        bot_noise_t2 = self.scan_bot_noise_and_entropy(text2)

        # FIX: Semantic threshold 55 se 65 kar diya
        is_spam = "YES" if (semantic_score >= 65.0 or fuzzy_score >= 65.0) else "NO"

        return {
            "semantic": semantic_score,
            "fuzzy": fuzzy_score,
            "noise_1": bot_noise_t1,
            "noise_2": bot_noise_t2,
            "is_bot": is_spam
        }

# Global object create kar rahe hain taaki pure streamlit dashboard par kahi bhi use ho sake
vasuki_brain = VasukiAIIntelligence()
# ==========================================
