import google.generativeai as genai
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

_configured = False


def _configure():
    global _configured
    if not _configured:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        _configured = True


def chat_long(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
    max_tokens: int = 8192,
) -> str:
    _configure()
    try:
        model = genai.GenerativeModel(
            settings.LLM_LONG_MODEL,
            system_instruction=system_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        response = model.generate_content(user_prompt)
        return response.text
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        raise


def chat_long_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.4,
) -> dict:
    text = chat_long(system_prompt, user_prompt, temperature=temperature)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
