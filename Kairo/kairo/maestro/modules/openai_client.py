"""
openai_client.py
Cliente para comunicação com a API da OpenAI
"""

import os
import json
from openai import OpenAI
from typing import Dict, Any, Optional

from modules.logger import get_logger
from config import OPENAI_CONFIG

class OpenAIClient:
    """
    Cliente para comunicação com a API da OpenAI
    """

    def __init__(self):
        self.logger = get_logger('openai_client')

        # Configurações
        self.api_key = OPENAI_CONFIG.get("api_key")
        self.model = OPENAI_CONFIG.get("model", "gpt-4-turbo")
        self.streaming_model = OPENAI_CONFIG.get("streaming_model", "gpt-4-turbo")
        self.temperature = OPENAI_CONFIG.get("temperature", 0.7)
        self.max_tokens = OPENAI_CONFIG.get("max_tokens", 1500)

        self.client = None
        self.is_connected = False

    def initialize(self):
        """Inicializa o cliente OpenAI"""
        try:
            self.logger.info("Inicializando OpenAIClient...")
            if not self.api_key:
                raise Exception("API key da OpenAI não foi fornecida.")

            self.client = OpenAI(api_key=self.api_key)
            self._test_connection()
            self.is_connected = True
            self.logger.info("OpenAIClient inicializado com sucesso.")

        except Exception as e:
            self.logger.error(f"Erro ao inicializar OpenAIClient: {e}")
            self.is_connected = False
            raise

    def _test_connection(self):
        """Testa a conexão com a API da OpenAI"""
        try:
            self.logger.info("Testando conexão com a API da OpenAI...")
            self.client.models.list()
            self.logger.info("Conexão com a OpenAI bem-sucedida.")
        except Exception as e:
            self.logger.error(f"Não foi possível conectar à OpenAI: {e}")
            raise

    def stream_prompt(self, prompt: str):
        """
        Envia um prompt para a API da OpenAI e faz o streaming da resposta,
        processando e retornando objetos JSON completos assim que são recebidos.
        """
        if not self.is_connected:
            self.logger.error("Cliente não conectado à OpenAI.")
            return

        self.logger.info(f"Enviando prompt para streaming com o modelo {self.streaming_model}...")
        try:
            stream = self.client.chat.completions.create(
                model=self.streaming_model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            buffer = ""
            decoder = json.JSONDecoder()
            for chunk in stream:
                delta_content = chunk.choices[0].delta.content
                if delta_content is None:
                    continue

                buffer += delta_content

                pos = 0
                while pos < len(buffer):
                    try:
                        while pos < len(buffer) and buffer[pos].isspace():
                            pos += 1
                        if pos == len(buffer):
                            break

                        obj, end_pos = decoder.raw_decode(buffer[pos:])
                        self.logger.debug(f"JSON completo recebido: {obj}")
                        yield obj
                        pos += end_pos
                    except json.JSONDecodeError:
                        break

                buffer = buffer[pos:]

        except Exception as e:
            self.logger.error(f"Erro durante o streaming da OpenAI: {e}")
            yield {"error": "Ocorreu um erro durante o streaming.", "details": str(e)}

    def shutdown(self):
        """Encerra o cliente OpenAI"""
        self.logger.info("OpenAIClient encerrado.")
