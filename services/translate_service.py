"""
Google Cloud Translation API Service for VoteWise AI

Provides multilingual election guidance support.
Features:
- Translate election content for voters
- Dynamic language switching
- Support for English and Hindi
- Fallback for API unavailability
"""

import requests
import json
from typing import Optional, Dict, Any, List
from config import Config


class TranslateService:
    """Google Cloud Translation API integration."""

    SUPPORTED_LANGUAGES = {
        "en": "English",
        "hi": "Hindi",
        "bn": "Bengali",
        "ta": "Tamil",
        "te": "Telugu",
        "mr": "Marathi",
        "kn": "Kannada",
        "gu": "Gujarati",
        "ml": "Malayalam",
        "pa": "Punjabi",
        "or": "Odia",
        "as": "Assamese",
        "ur": "Urdu",
    }

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY  # Using for potential translation
        self._initialized = False
        self._init_translate()

    def _init_translate(self):
        """Initialize translation service."""
        try:
            from google.cloud import translate_v2 as translate
            import os

            if Config.FIREBASE_CREDENTIALS_PATH and os.path.exists(
                Config.FIREBASE_CREDENTIALS_PATH
            ):
                self.client = translate.Client()
                self._initialized = True
            else:
                self.client = None
        except Exception as e:
            print(f"Translation API init error: {e}")
            self.client = None

    def translate(
        self, text: str, target_language: str = "hi", source_language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Translate text to target language.

        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code

        Returns:
            Translation result with original and translated text
        """
        if (
            target_language == source_language
            or target_language == "en"
            and source_language == "en"
        ):
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": source_language,
                "target_language": target_language,
                "detected_language": source_language,
            }

        if self.client and self._initialized:
            try:
                result = self.client.translate(
                    text,
                    target_language=target_language,
                    source_language=source_language,
                )

                return {
                    "original_text": text,
                    "translated_text": result["translatedText"],
                    "source_language": result.get(
                        "detectedSourceLanguage", source_language
                    ),
                    "target_language": target_language,
                }
            except Exception as e:
                print(f"Translation error: {e}")

        return self._mock_translate(text, target_language, source_language)

    def translate_batch(
        self, texts: List[str], target_language: str = "hi"
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts at once.

        Args:
            texts: List of texts to translate
            target_language: Target language code

        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.translate(text, target_language)
            results.append(result or {"original_text": text, "translated_text": text})
        return results

    def detect_language(self, text: str) -> Optional[str]:
        """
        Detect language of given text.

        Args:
            text: Text to analyze

        Returns:
            Language code
        """
        if self.client and self._initialized:
            try:
                result = self.client.detect_language(text)
                return result.get("language")
            except Exception:
                pass

        return self._detect_with_rules(text)

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages.

        Returns:
            List of language codes and names
        """
        return [
            {"code": code, "name": name}
            for code, name in self.SUPPORTED_LANGUAGES.items()
        ]

    def translate_election_content(
        self, content: Dict[str, Any], target_language: str = "hi"
    ) -> Dict[str, Any]:
        """
        Translate full election content object.

        Args:
            content: Election content dictionary
            target_language: Target language

        Returns:
            Translated content
        """
        translated = {"original": content, "language": target_language}

        text_fields = ["title", "intro", "description", "content"]
        for field in text_fields:
            if field in content and content[field]:
                result = self.translate(content[field], target_language)
                if result:
                    translated[field] = result["translated_text"]

        if "steps" in content and content["steps"]:
            translated_steps = []
            for step in content["steps"]:
                if isinstance(step, dict):
                    step_result = self.translate(
                        step.get("description", ""), target_language
                    )
                    translated_step = {
                        "step": step.get("step"),
                        "description": step_result["translated_text"]
                        if step_result
                        else step.get("description", ""),
                    }
                    translated_steps.append(translated_step)
                else:
                    result = self.translate(str(step), target_language)
                    translated_steps.append(
                        result["translated_text"] if result else str(step)
                    )
            translated["steps"] = translated_steps

        if "tips" in content and content["tips"]:
            tips_result = self.translate_batch(content["tips"], target_language)
            translated["tips"] = [t["translated_text"] for t in tips_result]

        return translated

    def _mock_translate(self, text: str, target: str, source: str) -> Dict[str, Any]:
        """Mock translation when API unavailable."""
        mock_translations = {
            "hi": {
                "How do I register to vote?": "मैं मतदाता के रूप में कैसे पंजीकरण करूं?",
                "How do I vote?": "मैं कैसे वोट करूं?",
                "What ID do I need?": "मुझे क्या ID चाहिए?",
                "Where is my polling booth?": "मेया मतदान केंद्र कहाँ है?",
                "Registration": "पंजीकरण",
                "Voting": "मतदान",
                "ID Required": "ID आवश्यक",
            }
        }

        translated = mock_translations.get(target, {}).get(text)

        return {
            "original_text": text,
            "translated_text": translated or f"[{target.upper()}] {text}",
            "source_language": source,
            "target_language": target,
        }

    def _detect_with_rules(self, text: str) -> str:
        """Simple rule-based language detection."""
        hindi_chars = set("अआइईउऊऋएऐओऔकखगघचछजझटठडढणतथदधनपफबभयरलवहशषस")
        hindi_count = sum(1 for c in text if c in hindi_chars)

        if hindi_count > len(text) * 0.3:
            return "hi"
        return "en"


class ElectionContentTranslator:
    """Specialized translator for election content."""

    def __init__(self):
        self.translator = TranslateService()

    def translate_faqs(
        self, faqs: List[Dict[str, Any]], language: str = "hi"
    ) -> List[Dict[str, Any]]:
        """Translate FAQ content."""
        translated_faqs = []

        for faq in faqs:
            translated = {"id": faq.get("id")}

            if "question" in faq:
                result = self.translator.translate(faq["question"], language)
                translated["question"] = result["translated_text"]

            if "answer" in faq:
                result = self.translator.translate(faq["answer"], language)
                translated["answer"] = result["translated_text"]

            translated["category"] = faq.get("category")
            translated["tags"] = faq.get("tags", [])
            translated["language"] = language

            translated_faqs.append(translated)

        return translated_faqs

    def translate_timeline(
        self, timeline: Dict[str, Any], language: str = "hi"
    ) -> Dict[str, Any]:
        """Translate timeline content."""
        translated = {"id": timeline.get("id")}

        if "title" in timeline:
            result = self.translator.translate(timeline["title"], language)
            translated["title"] = result["translated_text"]

        date_fields = [
            "registration_start",
            "registration_deadline",
            "polling_date",
            "result_date",
        ]
        for field in date_fields:
            if field in timeline:
                translated[field] = timeline[field]

        if "description" in timeline:
            result = self.translator.translate(timeline["description"], language)
            translated["description"] = result["translated_text"]

        translated["language"] = language
        return translated

    def translate_election_steps(
        self, steps: List[Dict], language: str = "hi"
    ) -> List[Dict]:
        """Translate election process steps."""
        translated_steps = []

        for step in steps:
            translated_step = {}

            if isinstance(step, dict):
                if "title" in step:
                    result = self.translator.translate(step["title"], language)
                    translated_step["title"] = result["translated_text"]

                if "description" in step:
                    result = self.translator.translate(step["description"], language)
                    translated_step["description"] = result["translated_text"]

                translated_step.update(
                    {k: v for k, v in step.items() if k not in ["title", "description"]}
                )
            else:
                result = self.translator.translate(str(step), language)
                translated_step["text"] = result["translated_text"]

            translated_steps.append(translated_step)

        return translated_steps

    def get_language_name(self, code: str) -> str:
        """Get full language name from code."""
        return self.translator.SUPPORTED_LANGUAGES.get(code, code.upper())


translate_service = TranslateService()
election_translator = ElectionContentTranslator()
