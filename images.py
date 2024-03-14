import os
from openai import OpenAI

API_KEY = os.getenv("API_KEY") or "sk-XXXX"

client = OpenAI(
    api_key=API_KEY
)

response = client.images.generate(
  model="dall-e-3",
  prompt="Minimalist logo for Project-MoonShine; an Ai company that creates AI companion apps.",
  size="1024x1024",
  quality="hd",
  n=1,
)

image_url = response.data[0].url

print(response)