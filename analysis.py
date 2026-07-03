import streamlit as st
from collections import Counter
from datetime import datetime
import pandas as pd
import uuid

def init_sidebar_history():
    if 'scan_history' not in st.session_state:
        st.session_state.scan_history = []

def show_sidebar_share():
    with st.sidebar:
        st.title("HumbotiX Ai")
        st.markdown("---")

        if st.session_state.scan_history:
            st.subheader("🔍 Recent Scans")
            for scan in st.session_state.scan_history[-5:][::-1]:
                st.markdown(f"*{scan['username']}* - {scan['bot_score']}% Bot")
                st.progress(scan['bot_score']/100)

            if st.button("📤 Share Last Scan", use_container_width=True, key="sidebar_share"):
                last = st.session_state.scan_history[-1]
                share_text = f"🤖 Vasuki AI Analysis\n\nUser: {last['username']}\nBot Score: {last['bot_score']}%\nVerdict: {last['verdict']}\n\nCheck: your-app-link.streamlit.app"
                st.code(share_text, language=None)
                st.success("Copied! Share karo")
        else:
            st.info("Scan karo. Results yahan aayenge.")

def run_all_analysis(username, tweet_times_list, tweet_text_list, tpd, age, last_tweet, total_posts, verified, flags):

    # Har scan ko unique ID do
    scan_id = str(uuid.uuid4())[:8]

    # Card start
    with st.container():
        st.markdown("---")
        col1, col2 = st.columns([6, 1])
        with col1:
            st.header(f"🔬 Analysis: {username}")
        with col2:
            # HAR CARD ME CHOTA SHARE BUTTON
            if st.button("📤", key=f"share_{scan_id}", help="Share this scan"):
                share_text = f"🤖 Vasuki AI Bot Scan\nUser: {username}\nAnalyzed on Vasuki AI"
                st.toast("Copied to clipboard!")
                st.code(share_text, language=None)

        # 1. TIME HEATMAP
        st.subheader("1️⃣ Time Heatmap")
        if tweet_times_list:
            hours = []
            for t in tweet_times_list:
                try:
                    dt = datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S")
                    hours.append(dt.hour)
                except:
                    continue

            if hours:
                hour_count = Counter(hours)
                df = pd.DataFrame({
                    'Hour': range(24),
                    'Tweets': [hour_count.get(h, 0) for h in range(24)]
                })
                st.bar_chart(df.set_index('Hour'))
                peak_hour = max(hour_count, key=hour_count.get)
                st.caption(f"Peak: {peak_hour}:00 hrs | {hour_count[peak_hour]} tweets")
            else:
                st.warning("No valid timestamps")
        else:
            st.warning("No timestamp data")

        st.markdown("---")

        # 2. CONTENT DUPLICATE CHECK
        st.subheader("2️⃣ Content Duplicate Check")
        dup_percent = 0
        if tweet_text_list:
            text_counts = Counter(tweet_text_list)
            duplicates = {k: v for k, v in text_counts.items() if v > 1}

            if duplicates:
                dup_percent = (sum(duplicates.values()) - len(duplicates)) / len(tweet_text_list) * 100
                st.error(f"Found {len(duplicates)} duplicates | {dup_percent:.1f}% repeated")
                with st.expander("View duplicates"):
                    for text, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:3]:
                        st.write(f"*{count}x:* {text[:80]}...")
            else:
                st.success("✅ All tweets unique")
        else:
            st.warning("No tweet text data")

        st.markdown("---")

        # 3. INTERVAL ANALYSIS
        st.subheader("3️⃣ Interval Analysis")
        avg_interval = 0
        min_interval = 0
        if len(tweet_times_list) >= 2:
            try:
                timestamps = [datetime.strptime(str(t), "%Y-%m-%d %H:%M:%S") for t in tweet_times_list]
                timestamps.sort()
                intervals = [(timestamps[i] - timestamps[i-1]).total_seconds() / 60 for i in range(1, len(timestamps))]

                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    min_interval = min(intervals)

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Avg Gap", f"{avg_interval:.1f} min")
                    c2.metric("Min Gap", f"{min_interval:.1f} min")
                    c3.metric("Posts", len(tweet_times_list))

                    if min_interval < 1:
                        st.error("⚠️ Bot Alert: <1 min gaps detected")
                    elif avg_interval < 5:
                        st.warning("⚠️ High frequency posting")
                    else:
                        st.success("✅ Human-like intervals")
            except:
                st.error("Error parsing time intervals")
        else:
            st.warning("Need 2+ tweets for analysis")

        st.markdown("---")

        # 4. BOT SCORE + SIDEBAR SHARE BUTTON DATA SAVE
        st.subheader("4️⃣ Bot Score Calculator")

        score = 0
        reasons = []

        if tpd > 100: score += 30; reasons.append(f"TPD: {tpd}")
        elif tpd > 50: score += 20; reasons.append(f"TPD: {tpd}")
        elif tpd > 20: score += 10

        if age < 30 and total_posts > 1000: score += 25; reasons.append("New account, high posts")
        elif age < 90: score += 10

        if not verified: score += 10; reasons.append("Not verified")

        if dup_percent > 10: score += 20; reasons.append(f"{dup_percent:.0f}% duplicates")
        elif dup_percent > 5: score += 10

        score = min(score, 100)

        if score >= 70: verdict = "🔴 HIGH BOT PROBABILITY"; st.error(verdict)
        elif score >= 40: verdict = "🟡 SUSPICIOUS"; st.warning(verdict)
        else: verdict = "🟢 LIKELY HUMAN"; st.success(verdict)

        st.metric("Final Bot Score", f"{score}%")

        if reasons:
            with st.expander("Scoring reasons"):
                for r in reasons: st.write(f"• {r}")

        # SIDEBAR ME SAVE KARO - Ye 4th feature hai
        st.session_state.scan_history.append({
            'username': username,
            'bot_score': score,
            'verdict': verdict,
            'scan_id': scan_id,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        st.markdown("---")
        st.caption(f"Scan ID: {scan_id} | Powered by Vasuki AI 🧠")
