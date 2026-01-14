"""
Grammar Correction Module
Handles AI-powered grammar correction using Google Gemini
Includes retry logic, rate limiting, and proper error handling
"""

import os
import time
import random
from typing import Optional, Dict, Any, List

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GrammarCorrectionError(Exception):
    """Custom exception for grammar correction errors"""
    pass


class RateLimitError(GrammarCorrectionError):
    """Raised when API rate limit is exceeded"""
    pass


class GrammarCorrector:
    """
    Grammar correction using Google Gemini AI
    Implements retry logic with exponential backoff and jitter
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash",
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
    ):
        """
        Initialize the grammar corrector
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise GrammarCorrectionError("GEMINI_API_KEY not set")

        self.model_name = model_name
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.model = genai.GenerativeModel(self.model_name)

        # Generation config for deterministic grammar fixes
        # Increased max_output_tokens to handle longer text (paragraphs)
        self.generation_config = {
            "temperature": 0.2,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 8192,  # Increased from 512 to handle longer text
        }

    def _calculate_delay(self, attempt: int) -> float:
        """Exponential backoff with jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter

    def _build_prompt(self, text: str) -> str:
        """
        Build a strict grammar-correction prompt.
        Ensures output contains ONLY the corrected text.
        Handles both single sentences and multi-line paragraphs.
        """
        return (
            "You are a professional grammar and spelling correction engine.\n"
            "Your task is to correct all grammar, spelling, and punctuation errors in the text below.\n"
            "Preserve the original formatting, line breaks, and structure.\n"
            "Return ONLY the corrected text without any explanations, comments, or additional formatting.\n"
            "Do not add introductory phrases like 'Here is' or 'Corrected version'.\n\n"
            f"Text to correct:\n{text}\n\n"
            "Corrected text:"
        )

    def _extract_text(self, response) -> str:
        """
        Safely extract text from Gemini response
        """
        if not response:
            return ""

        if hasattr(response, "text") and response.text:
            return response.text.strip()

        # Fallback for candidate-based responses
        try:
            return response.candidates[0].content.parts[0].text.strip()
        except Exception:
            return ""

    def _execute_with_retry(self, text: str) -> str:
        """
        Execute grammar correction with retry logic
        """
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                prompt = self._build_prompt(text)

                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                )

                corrected = self._extract_text(response)
                if not corrected:
                    raise GrammarCorrectionError("Empty response from AI model")

                return corrected

            except Exception as e:
                msg = str(e).lower()

                if any(k in msg for k in ("429", "quota", "rate limit")):
                    last_error = RateLimitError(str(e))
                elif any(k in msg for k in ("api key", "authentication")):
                    raise GrammarCorrectionError(f"API authentication error: {e}")
                else:
                    last_error = GrammarCorrectionError(f"AI generation failed: {e}")

                if attempt < self.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    print(
                        f"Retrying in {delay:.2f}s "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    time.sleep(delay)

        raise last_error or GrammarCorrectionError(
            "Grammar correction failed after all retries"
        )

    def correct(self, text: str) -> Dict[str, Any]:
        """
        Correct grammar in text (can be single sentence or multiple paragraphs)
        """
        if not text or len(text.strip()) < 3:
            return {
                "success": False,
                "original": text,
                "error": "Please enter text with at least 3 characters.",
            }

        try:
            corrected = self._execute_with_retry(text)
            return {
                "success": True,
                "original": text,
                "corrected": corrected,
            }

        except RateLimitError:
            return {
                "success": False,
                "original": text,
                "error": (
                    "Rate limit exceeded. Please try again later or "
                    "check your quota at https://aistudio.google.com/"
                ),
            }

        except GrammarCorrectionError as e:
            return {
                "success": False,
                "original": text,
                "error": str(e),
            }

        except Exception as e:
            return {
                "success": False,
                "original": text,
                "error": f"Unexpected error: {e}",
            }

    def correct_batch(self, sentences: List[str]) -> List[Dict[str, Any]]:
        """
        Correct multiple sentences with throttling
        """
        results = []

        for i, sentence in enumerate(sentences):
            results.append(self.correct(sentence))
            if i < len(sentences) - 1:
                time.sleep(0.5)

        return results


def correct_grammar(sentence: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience wrapper for single sentence correction
    """
    return GrammarCorrector(api_key=api_key).correct(sentence)


if __name__ == "__main__":
    test_sentences = [
        "he walk to the store yesteday",
        "She don't likes pizza",
        "They was going to the park",
    ]

    print("Testing Grammar Corrector...\n")

    for s in test_sentences:
        result = correct_grammar(s)
        print(f"Original : {s}")
        print(
            f"Corrected: {result['corrected']}"
            if result["success"]
            else f"Error    : {result['error']}"
        )
        print()
