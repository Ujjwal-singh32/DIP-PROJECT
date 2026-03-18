"""
llm_client.py
─────────────
Google Gemini API wrapper with both streaming and non-streaming support.
"""

from typing import Generator, List

import google.generativeai as genai
from google.generativeai.types import HarmBlockThreshold, HarmCategory

from backend.config import settings
from utils.logger import logger

SYSTEM_PROMPT = """You are LexAI, an expert Indian legal assistant powered by a Retrieval-Augmented Generation system.

You will be given LEGAL REFERENCES retrieved from a database of Indian law sections.
Your task is to:
  1. Answer the user's legal question clearly and accurately in 6-8 lines.
  2. Base your answer STRICTLY on the provided legal references.
  3. Always cite the exact Act name and Section number for every claim.
  4. Use clear, accessible language while maintaining legal precision.
  5. If the question cannot be answered from the provided references, say so honestly.

Answer format:
─────────────
**Answer:** [Direct, concise answer in 2-3 sentences]

**Legal Basis:**
• [Act Name], Section [Number] – [Section Title]
  > "[Short quoted clause text — max 2 lines]"
  [Brief explanation]

**Note:** [One line caveat or practical advice]
─────────────
Keep answers concise. Always recommend consulting a qualified legal professional.
"""


class GeminiClient:
    def __init__(self) -> None:
        logger.info(f"Initialising Gemini client | model={settings.gemini_model}")
        genai.configure(api_key=settings.gemini_api_key)

        self._safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        self._model = genai.GenerativeModel(
            model_name=settings.gemini_model,
            system_instruction=SYSTEM_PROMPT,
            safety_settings=self._safety_settings,
        )
        logger.info("Gemini client ready")

    def _build_message(self, context: str, query: str) -> str:
        return (
            f"=== RETRIEVED LEGAL REFERENCES ===\n"
            f"{context}\n\n"
            f"=== USER QUESTION ===\n"
            f"{query}"
        )

    def _build_history(self, history: List[dict]) -> list:
        gemini_history = []
        for turn in (history or []):
            role = "user" if turn["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [turn["content"]]})
        return gemini_history

    def generate(
        self,
        context: str,
        query: str,
        history: List[dict] | None = None,
    ) -> str:
        """Non-streaming generation — returns full answer string."""
        user_message = self._build_message(context, query)
        gemini_history = self._build_history(history or [])
        try:
            chat = self._model.start_chat(history=gemini_history)
            response = chat.send_message(user_message)
            answer = response.text
            logger.info(f"Gemini generated {len(answer)} chars for: '{query[:60]}'")
            return answer
        except Exception as exc:
            logger.error(f"Gemini API error: {exc}")
            raise RuntimeError(f"LLM generation failed: {exc}") from exc

    def generate_stream(
        self,
        context: str,
        query: str,
        history: List[dict] | None = None,
    ) -> Generator[str, None, None]:
        """
        Streaming generation — yields text chunks as they arrive.

        Usage:
            for chunk in client.generate_stream(context, query, history):
                print(chunk, end="", flush=True)
        """
        user_message = self._build_message(context, query)
        gemini_history = self._build_history(history or [])
        try:
            chat = self._model.start_chat(history=gemini_history)
            response = chat.send_message(user_message, stream=True)
            full_text = ""
            for chunk in response:
                if chunk.text:
                    full_text += chunk.text
                    yield chunk.text
            logger.info(
                f"Gemini streamed {len(full_text)} chars for: '{query[:60]}'"
            )
        except Exception as exc:
            logger.error(f"Gemini stream error: {exc}")
            yield f"\n\n⚠️ Error generating response: {exc}"