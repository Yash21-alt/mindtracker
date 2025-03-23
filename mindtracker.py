import streamlit as st
import pandas as pd
import google.generativeai as genai
import os
import matplotlib.pyplot as plt
import datetime

GEMINI_API_KEY = "" 
genai.configure(api_key=GEMINI_API_KEY)

data_file = "mental_health_logs.csv"

def load_data():
    if os.path.exists(data_file):
        return pd.read_csv(data_file)
    return pd.DataFrame(columns=["Date", "User Input", "AI Response", "Mood", "Mental Health Score", "Suggestions", "Emotion Trigger"])

def save_data(data):
    data.to_csv(data_file, index=False)

def get_ai_response(user_input, past_conversations):
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(f"Analyze this mental health input: {user_input} and provide a thoughtful response.")
    
    return response.text.strip()

def classify_emotion_trigger(user_input):
    triggers = {
        "Work/Studies Stress": ["exam", "deadline", "study", "work", "project", "stress", "assignment", "burnout"],
        "Relationships": ["friend", "family", "love", "relationship", "breakup", "fight", "lonely"],
        "Loneliness & Isolation": ["alone", "isolated", "ignored", "nobody", "no one"],
        "Self-Doubt & Low Confidence": ["not good enough", "fail", "useless", "failure", "doubt", "hopeless"],
        "Anxiety & Overthinking": ["worry", "anxious", "overthinking", "nervous", "scared", "fear"],
        "Excitement & Achievements": ["happy", "excited", "promotion", "success", "win", "proud"]
    }
    
    for category, keywords in triggers.items():
        if any(word in user_input.lower() for word in keywords):
            return category
    
    return "General"

st.title("🧠 AI-Powered Mental Health Tracker")
st.subheader("A safe space to track your emotions and receive guidance")

df = load_data()
past_conversations = df.tail(5).to_dict(orient="records")

user_input = st.text_area("Describe how you feel:")

if st.button("Submit"):
    if user_input:
        ai_response = get_ai_response(user_input, past_conversations)
        detected_mood = classify_emotion_trigger(user_input)
        mental_health_score = len(user_input) % 10 + 1  
        suggestion = "Stay mindful and take care of yourself!"  
        new_entry = pd.DataFrame({
            "Date": [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            "User Input": [user_input],
            "AI Response": [ai_response],
            "Mood": [detected_mood],
            "Mental Health Score": [mental_health_score],
            "Suggestions": [suggestion],
            "Emotion Trigger": [detected_mood]
        })
        
        df = pd.concat([df, new_entry], ignore_index=True)
        save_data(df)
        
        st.success("Entry saved successfully!")
        st.write("**AI Response:**", ai_response)
        st.write("**Detected Emotion Trigger:**", detected_mood)
        st.write("**Mental Health Score:**", mental_health_score, "/ 10")
        st.write("**Wellness Tip:**", suggestion)

if st.checkbox("Show Past Conversations"):
    if not df.empty:
        st.dataframe(df.tail(10))
    else:
        st.write("No previous conversations recorded.")

if st.checkbox("Show Emotion Triggers Over Time"):
    if not df.empty:
        trigger_counts = df["Emotion Trigger"].value_counts()
        fig, ax = plt.subplots()
        trigger_counts.plot(kind="bar", ax=ax, color=["blue", "red", "green", "purple", "orange"])
        ax.set_title("Emotion Triggers Over Time")
        ax.set_xlabel("Emotion Trigger")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    else:
        st.write("No data available yet.")


if st.checkbox("Daily Mental Health Tip"):
    st.info("Remember to take breaks and prioritize self-care. Small mindful moments can make a big difference. 💙")
