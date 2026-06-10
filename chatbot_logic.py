import time

def get_bot_response(user_message):
    user_message = user_message.lower()

    time.sleep(1.5)  # Wait 1.5 seconds before replying (adjust as needed)

    # General greetings
    if any(greet in user_message for greet in ["hello", "hi", "hey"]):
        return "Hello! How can I assist you with your health today?"

    # Fever and cold symptoms
    if "fever" in user_message or "cold" in user_message:
        return "It sounds like you're experiencing fever and cold. Please stay hydrated, rest well, and consider taking paracetamol if the fever persists. If symptoms continue for more than 2 days, consult a doctor."

    # Headache
    if "headache" in user_message:
        return "For a headache, try resting in a quiet room and stay hydrated. If the pain is severe or persistent, you should consult a healthcare provider."

    # COVID-like symptoms
    if "cough" in user_message and "taste" in user_message:
        return "These symptoms are commonly associated with COVID-19. Please consider getting tested and isolate yourself from others."

    # Emergency
    if "emergency" in user_message or "urgent" in user_message:
        return "This seems serious. Please call your local emergency number or visit the nearest hospital immediately."

    # Heart-related concerns
    if "chest pain" in user_message or "breathless" in user_message:
        return "Chest pain and breathlessness can be signs of heart problems. Seek medical attention immediately. Do not ignore these symptoms."

    if "heart" in user_message and "risk" in user_message:
        return "If you're concerned about your heart risk, I recommend a heart risk prediction test. Maintain a healthy lifestyle and consult your doctor for screening."

    # Diabetes concerns
    if "sugar level" in user_message or "diabetes" in user_message:
        return "Diabetes management includes eating a balanced diet, regular exercise, and monitoring blood sugar levels. Let me know if you'd like to predict your diabetes risk."

    if "my sugar is" in user_message or "glucose level" in user_message:
        return "That sounds like a glucose level report. Please monitor it regularly and consult your doctor if it's too high or too low."

    # Drug/medicine-related
    if "medicine for" in user_message or "drug for" in user_message:
        return "Please provide the condition you're seeking a medicine for. I can recommend common treatments, but always verify with a doctor."

    if "can i take" in user_message:
        return "It's best to consult a pharmacist or doctor before taking any medicine, especially if you're on other medications."

    # Goodbye
    if "bye" in user_message or "goodbye" in user_message:
        return "Take care! Wishing you good health."

    # Default fallback
    return "I'm not sure I understand that fully. Could you describe your symptoms or question in a different way?"
