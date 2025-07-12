from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
load_dotenv("env/.env")

import PIL.Image
clothes = PIL.Image.open("images/clothes/clothes_2.png")

client = genai.Client()

# Step 1: Analyze the clothes image to describe the pet's clothing
clothes_description_prompt = """Please analyze these Vietnamese pet clothes in detail. Focus on colors and patterns for each part of the clothing.

Note that these clothes are made of silk material. 

Provide a detailed description that could be used as a prompt for generating similar clothing in an image. Be specific about the visual elements, colors, textures, and style details."""

clothes_response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[clothes_description_prompt, clothes],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT'],
        temperature=0.0,
    )
)

# Print the generated clothes description
print("Clothes Description for Image Generation:")
print("=" * 50)
print(clothes_response.text)
print("=" * 50)