import google.generativeai as genai
import os

# You would get your API key from Google AI Studio
genai.configure(api_key="YOUR_GEMINI_API_KEY")

# 1. Setup the "Brain" with specific instructions
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction="You are a home automation agent. Respond only with JSON commands."
)

# 2. Start a chat session
chat = model.start_chat()

# 3. Simulate a natural language command
response = chat.send_message("I'm heading to bed, turn off the lab lights.")

print(response.text)
# Output might be: {"action": "ESP_NOW_SEND", "target": "CoreS3", "cmd": "LIGHTS_OFF"}