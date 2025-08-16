import os
import json
import openai
from openai import OpenAI
from config import OPENAI_CONFIG
from modules.logger import get_logger

class OpenAIClient:
    def __init__(self):
        self.logger = get_logger('openai_client')
        self.api_key = OPENAI_CONFIG.get("api_key")
        self.model = OPENAI_CONFIG.get("model")
        self.client = None
        self.connected = False

    def initialize(self):
        if not self.api_key:
            self.logger.error("OpenAI API key not found in environment variables.")
            return

        try:
            self.client = OpenAI(api_key=self.api_key)
            self.test_connection()
            if self.connected:
                self.logger.info(f"OpenAIClient initialized successfully for model {self.model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            self.connected = False

    def test_connection(self):
        try:
            self.client.models.list()
            self.logger.info("Successfully connected to OpenAI API.")
            self.connected = True
        except Exception as e:
            self.logger.error(f"Failed to connect to OpenAI API: {e}")
            self.connected = False

    def send_prompt(self, prompt, temperature=None, max_tokens=None):
        if not self.is_running():
            self.logger.error("OpenAI client is not connected.")
            return {"error": "Client not connected"}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature if temperature is not None else OPENAI_CONFIG.get("temperature", 0.7),
                max_tokens=max_tokens if max_tokens is not None else OPENAI_CONFIG.get("max_tokens", 1500),
                response_format={"type": "json_object"}
            )
            response_content = response.choices[0].message.content
            return json.loads(response_content)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to decode JSON response from OpenAI: {e}")
            self.logger.error(f"Raw response: {response_content}")
            return {"error": "Invalid JSON response from LLM"}
        except Exception as e:
            self.logger.error(f"Error sending prompt to OpenAI: {e}")
            return {"error": str(e)}

    def is_running(self):
        return self.client is not None and self.connected

    def shutdown(self):
        self.logger.info("Shutting down OpenAIClient.")
        self.client = None
        self.connected = False
