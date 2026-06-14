import os
import base64
import json

try:
    from google import genai  # pyrefly: ignore [missing-import]
    from google.genai import types  # pyrefly: ignore [missing-import]
except ImportError:
    genai = None
    types = None

def get_gemini_client():
    if genai is None:
        print("google-genai library is not installed.")
        return None
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)
    return None

def generate_text_gemini(prompt: str, schema_class=None) -> dict:
    """
    Generate structured text from Gemini. Falls back to standard generation if schema fails.
    """
    client = get_gemini_client()
    if not client:
        print("Gemini API key not configured or google-genai library missing.")
        return {}
        
    try:
        config = None
        if schema_class and types is not None:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_class
            )
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        
        # Parse JSON output
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("Failed to decode JSON from Gemini response:", response.text)
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return {}
            
    except Exception as e:
        print(f"Gemini Text Generation Error: {e}")
        return {}

def generate_multimodal_gemini(prompt: str, image_base64: str, schema_class=None) -> dict:
    """
    Generate structured json from image analysis using Gemini 2.5 Flash.
    """
    client = get_gemini_client()
    if not client:
        print("Gemini API key not configured or google-genai library missing.")
        return {}
        
    try:
        image_bytes = base64.b64decode(image_base64)
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        ) if types is not None else None
        
        if image_part is None:
            return {}
            
        config = None
        if schema_class and types is not None:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=schema_class
            )
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[image_part, prompt],
            config=config
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print("Failed to decode JSON from Multimodal Gemini response:", response.text)
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return {}
            
    except Exception as e:
        print(f"Gemini Multimodal Generation Error: {e}")
        return {}
