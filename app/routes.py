from flask import Blueprint, request, jsonify
from transformers import pipeline
import re
from collections import defaultdict
import random

main_bp = Blueprint("main", __name__)

emotion_model = pipeline("text-classification", model="bhadresh-savani/bert-base-uncased-emotion")

@main_bp.route("/")
def home():
    return jsonify({"message": "Flask API is running!"})

@main_bp.route("/predict", methods=["POST"])
def predict():
    data = request.json
    text = data.get("text", "").strip()
    person = data.get("person", "").strip().lower()
    app = data.get("platform", "").strip().lower()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Extract processed text list
    if app == "whatsapp":
        lst = extract_whatsapp_chat(text, person) 
    elif app == "telegram":
        lst = extract_telegram_chat(text, person)
    elif app=="chat":
        st = emotion_model(text)[0]
        st=response_creator(st)
        return jsonify({"text":st})

    # Process each extracted text with emotion model
    list_text = [emotion_model(i)[0] for i in lst]  
    pi_data = piData(list_text)
    score = score_calc(list_text)
    emotion = emotional_state(score)
    key_words = keywords(lst)

    # Return Format
    format_text = {"piegraph":pi_data,"score":score,"keywords":key_words[:7],"emotion":emotion}

    return jsonify(format_text)  # Return results properly formatted

def piData(list_text):
    pi_dict = {"anger":0, "sadness":0, "fear":0, "disgust":0,"surprise":0, "joy":0}
    count = 0
    for i in list_text:
        count+=1
        pi_dict[i["label"]] += 1
    for i in pi_dict:
        if count==0:
            continue
        pi_dict[i] = round((pi_dict[i]/count)*100,2)
    return pi_dict

def score_calc(list_text):
    score = 0
    count = 0
    for i in list_text:
        if i["label"] == "anger":
            score += 80*i["score"]
        elif i["label"] == "sadness":
            score += 70*i["score"]
        elif i["label"] == "fear":
            score += 90*i["score"]
        elif i["label"] == "disgust":
            score += 85*i["score"]
        elif i["label"] == "joy":
            score -= 50*i["score"]
        elif i["label"] == "surprise":
            score += 20*i["score"]
        count += 1
    if count==0:
        return 0
    score //= count
    return round(((score+50)/130)*100,2)

def emotional_state(score):
    if (90<=score<100):
        return "Despair"
    elif (80<=score<90):
        return "Deep Sadness"
    elif (70<=score<80):
        return "Frustation"
    elif (60<=score<70):
        return "Disappointment"
    elif (50<=score<60):
        return "Indifference"
    elif (40<=score<50):
        return "Contentment"
    elif (30<=score<40):
        return "Satisfaction"
    elif (20<=score<30):
        return "Happiness"
    elif (10<=score<20):
        return "Excitment"
    elif (0<=score<10):
        return "Euphoria"
    
def keywords(lst):
    emotion_keywords = {
     "joy", "joyful", "enjoy", "enjoyed", "enjoying", "happiness", "happy", "happier", "happiest",
    "excite", "excited", "exciting", "love", "loved", "loving", "satisfy", "satisfied", "satisfying",
    "content", "contented", "contenting", "optimism", "optimistic", "gratitude", "grateful",
    "enthusiasm", "enthusiastic", "hope", "hopeful", "hoping", "pride", "proud", "amuse", "amused", "amusing",
    "relieve", "relieved", "relieving", "affection", "affectionate", "euphoria", "euphoric", "cheerful",
    "cheering", "delight", "delighted", "delighting", "trust", "trusting", "trusted", "awe", "awed", "awesome",
    "bliss", "blissful", "pleasure", "pleased", "pleasing", "admire", "admired", "admiring", "serenity",
    "serene", "confidence", "confident", "compassion", "compassionate", "relax", "relaxed", "relaxing",
    
    "sad", "sadder", "saddest", "sadness", "cry", "cried", "crying", "anger", "angry", "infuriate", "infuriated", "infuriating",
    "fear", "feared", "fearing", "scare", "scared", "scaring", "anxiety", "anxious", "frustrate", "frustrated", "frustrating",
    "disappoint", "disappointed", "disappointing", "despair", "desperate", "grief", "grieving", "envy", "envious",
    "jealous", "jealousy", "guilt", "guilty", "shame", "shamed", "ashamed", "lonely", "loneliness", "hate", "hated", "hating",
    "disgust", "disgusted", "disgusting", "hopeless", "hopelessness", "insecure", "insecurity", "embarrass", "embarrassed", "embarrassing",
    "worry", "worried", "worrying", "contempt", "contemptuous", "rage", "raging", "annoy", "annoyed", "annoying", "panic", "panicked",
    "resent", "resented", "resenting", "nervous", "nervousness", "mourn", "mourned", "mourning", "blame", "blamed", "blaming", "betray", "betrayed",
    
    "surprise", "surprised", "surprising", "curious", "curiosity", "anticipate", "anticipated", "anticipating",
    "confuse", "confused", "confusing", "shock", "shocked", "shocking", "indifferent", "indifference", "ambivalent",
    "puzzle", "puzzled", "puzzling", "interest", "interested", "interesting", "think", "thought", "thinking",
    "wonder", "wondered", "wondering", "expect", "expected", "expecting", "observe", "observed", "observing",
    "reflect", "reflected", "reflecting", "analyze", "analyzed", "analyzing", "consider", "considered", "considering",
    "speculate", "speculated", "speculating", "meditate", "meditated", "meditating", "focus", "focused", "focusing", 
    "alert", "alerted", "alerting", "contemplate", "contemplated", "contemplating", "observe", "observing", "stillness", "balance"}
    key_words = set()
    for i in lst:
        words = i.split()
        for word in words:
            if word.lower() in emotion_keywords:
                key_words.add(word.lower())
     
    return list(key_words)

        
def extract_whatsapp_chat(text, person):
    # Regular expression to match messages (handles any name)
    pattern = r"\[\d{2}/\d{2}/\d{4} \d{2}:\d{2} (?:AM|PM)\] ([^:]+): (.+)"

    # Dictionary to store messages by name
    messages = defaultdict(list)

    # Extract messages
    for match in re.findall(pattern, text):
        name, message = match
        messages[name].append(message.strip())

    # Print extracted messages
    for name, texts in messages.items():
        if name.lower() == person:
            return texts
    else:
        return []
def extract_telegram_chat(text, person):
    # Regular expression pattern to match Telegram messages
    pattern = r"([\w\s]+), \[(\d{2}-\d{2}-\d{4} \d{2}:\d{2})\]\n(.+)"

    # Dictionary to store messages by person
    messages = defaultdict(list)

    # Extract messages
    for match in re.findall(pattern, text):
        name, timestamp, message = match
        messages[name.strip()].append(message.strip())

    # Return messages for the requested person
    return messages.get(person, [])
    
def response_creator(st):
    label = st["label"]
    confidence = round(st["score"] * 100, 2)

    # Responses categorized by emotion
    responses = {
    "joy": [
        "You're radiating joy with {confidence}% confidence! 🌟",
        "I sense a lot of happiness — about {confidence}% sure you're feeling joyful! 😊",
        "It's a bright day for you! Joy is leading the way at {confidence}% certainty.",
        "Feeling joyful today? I’m {confidence}% confident you are! 🎉",
        "Happiness overload detected at {confidence}% certainty! 😄",
        "Smiles all around! You're {confidence}% filled with joy.",
        "That sparkle in your mood? {confidence}% chance it's pure joy! ✨",
        "Joy is contagious, and you're glowing at {confidence}% confidence.",
        "Looks like you’re on cloud nine with {confidence}% certainty! ☁️",
        "A happy heart beats strong — {confidence}% sure you're feeling joyful! ❤️",
        "Positive vibes incoming! Joy is leading at {confidence}%.",
        "The sun seems to be shining on your day — {confidence}% joyful! 🌞",
        "Radiating happiness with a {confidence}% confidence level!",
        "Laughter and smiles detected at {confidence}% certainty. 😆",
        "Your happiness meter is at {confidence}% today!",
        "I can feel the good vibes — {confidence}% sure you’re full of joy. 🎈",
        "What a cheerful day! You’re feeling joy with {confidence}% certainty.",
        "You’re glowing with positivity — {confidence}% joyful! 💫",
        "That happy energy? It’s at {confidence}% confidence right now.",
        "Seems like you're riding a wave of joy — {confidence}% sure! 🌊"
    ],
    "anger": [
        "Hmm, I can feel some tension. About {confidence}% sure you're feeling angry. 😠",
        "Take a deep breath — there's {confidence}% confidence you're experiencing anger.",
        "I detect some frustration with {confidence}% certainty. Hang in there! 💢",
        "Seems like you're a bit heated today — {confidence}% confident you're angry.",
        "Anger levels rising — about {confidence}% sure you're feeling mad. 🔥",
        "Is something bothering you? {confidence}% certainty of anger detected.",
        "Frustration detected at {confidence}% confidence. Try to stay calm. 🙏",
        "Tensions seem high — {confidence}% sure anger is taking over.",
        "I can sense the heat — {confidence}% confidence you're feeling upset.",
        "You seem irritated today — {confidence}% sure you're angry. 😤",
        "Storm clouds detected — {confidence}% sure you're feeling anger. 🌩️",
        "Feeling on edge? I'm {confidence}% sure you're experiencing anger.",
        "A bit of rage creeping in? {confidence}% confidence says so.",
        "The frustration is noticeable — about {confidence}% sure.",
        "Anger levels at {confidence}%, remember to breathe deeply. 😌",
        "Your emotions seem intense — {confidence}% confident it's anger.",
        "That fiery energy? {confidence}% chance it’s frustration. 🔥",
        "Looks like something upset you — {confidence}% confidence detected.",
        "I’m picking up some strong anger vibes — {confidence}% sure.",
        "Seems like you're having a tough moment — {confidence}% anger detected."
    ],
    "fear": [
        "Is something worrying you? I'm {confidence}% sure you're feeling fear. 😟",
        "Fear seems to be creeping in — about {confidence}% confidence detected.",
        "Stay strong! I sense fear with {confidence}% certainty.",
        "Looks like you're a bit anxious — I'm {confidence}% confident about that.",
        "Anxiety detected at {confidence}% certainty — it's okay to feel that way.",
        "You seem a bit on edge — {confidence}% sure you're experiencing fear.",
        "Worry levels rising — {confidence}% confidence you're feeling fear.",
        "It’s normal to feel scared — {confidence}% sure that’s happening now.",
        "I can sense some nervousness — {confidence}% confidence detected.",
        "A bit of fear in the air? {confidence}% sure you're anxious. 😰",
        "Uncertainty can be tough — I'm {confidence}% confident you're afraid.",
        "Courage is just fear that has said its prayers — you're at {confidence}% fear.",
        "You seem a little uneasy — about {confidence}% sure of that.",
        "Shadows of fear detected at {confidence}% certainty.",
        "Your heart seems to be racing — {confidence}% chance it's fear.",
        "It’s okay to be scared sometimes — {confidence}% confidence detected.",
        "Apprehension levels high — {confidence}% sure you're feeling fear.",
        "I’m sensing some worry — about {confidence}% certainty.",
        "There’s a bit of nervousness in the air — {confidence}% sure of it.",
        "That anxious feeling? I’m {confidence}% confident you're experiencing it."
    ],
    "sadness": [
        "I sense some sadness in you with {confidence}% certainty. Remember, it's okay to feel this way. 💙",
        "Feeling down? I’m {confidence}% sure you're experiencing sadness. 🥺",
        "Sending positive vibes your way — there's {confidence}% confidence you're feeling sad.",
        "I detect some sadness with {confidence}% certainty. You're not alone! 🌧️",
        "Your heart feels heavy — about {confidence}% sure you're feeling sad.",
        "A wave of sadness seems to be passing through — {confidence}% detected.",
        "Tough times never last — but I’m {confidence}% sure you’re feeling down right now.",
        "Cloudy skies ahead — {confidence}% confidence you're feeling sad. ☁️",
        "I sense some emotional weight — {confidence}% sure you're sad.",
        "A bit of sorrow detected at {confidence}% certainty. 🌧️",
        "It’s okay to feel blue — about {confidence}% sure you're experiencing that now.",
        "There’s a softness in your mood — {confidence}% sure it’s sadness.",
        "You seem to be carrying some emotional weight — {confidence}% sure.",
        "That lonely feeling? {confidence}% chance you're feeling it now.",
        "I’m here with you — sadness detected at {confidence}% confidence. 🤗",
        "The world feels heavier today — {confidence}% chance you're feeling sad.",
        "Melancholy vibes are present — {confidence}% certainty of sadness.",
        "A little tear in your heart? {confidence}% sure you’re feeling down.",
        "It’s okay not to be okay — {confidence}% confidence detected.",
        "Wishing you brighter days — you're at {confidence}% sadness."
    ],
    "default": [
        "I think you're feeling {label} with {confidence}% confidence today.",
        "Your mood seems to be {label}, with a {confidence}% certainty.",
        "I’m picking up on some {label} vibes — about {confidence}% sure.",
        "You seem to be experiencing {label} with {confidence}% confidence.",
        "Your emotions are leaning towards {label} — {confidence}% certainty.",
        "It looks like you're feeling {label} today, at {confidence}% confidence.",
        "I’m detecting {label} in your mood — about {confidence}% sure.",
        "There's a strong sense of {label} — {confidence}% detected.",
        "Your emotional state points to {label} with {confidence}% certainty.",
        "A wave of {label} is present — {confidence}% confidence.",
        "Seems like you're experiencing some {label} — {confidence}% sure.",
        "Feeling a bit of {label}? I’m {confidence}% certain.",
        "Your vibes hint at {label} — {confidence}% detected.",
        "I’m sensing a mood of {label} today — {confidence}% confidence.",
        "Could it be {label}? I’m about {confidence}% sure.",
        "Your energy reflects {label} — {confidence}% certainty.",
        "The atmosphere suggests {label} — around {confidence}% sure.",
        "I’m getting {label} signals with {confidence}% confidence.",
        "Your current mood seems to be {label}, at {confidence}% certainty.",
        "Picking up on some {label} vibes — {confidence}% confident."
    ]
}


    # Choose responses based on label or use default
    selected_responses = responses.get(label, responses["default"])
    response_template = random.choice(selected_responses)

    return response_template.format(label=label, confidence=confidence)
