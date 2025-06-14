"""
ollama_client.py
Cliente para comunicação com Ollama local
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import OLLAMA_CONFIG
from modules.logger import get_logger, log_error

class OllamaClient:
    """
    Cliente para comunicação com servidor Ollama local
    Responsável por enviar prompts e receber respostas do modelo de linguagem
    """
    
    def __init__(self):
        self.logger = get_logger('ollama_client')
        
        # Configurações
        self.base_url = OLLAMA_CONFIG["base_url"]
        self.model = OLLAMA_CONFIG["model"]
        self.timeout = OLLAMA_CONFIG["timeout"]
        self.max_retries = OLLAMA_CONFIG["max_retries"]
        self.temperature = OLLAMA_CONFIG["temperature"]
        self.max_tokens = OLLAMA_CONFIG["max_tokens"]
        
        # Session HTTP com retry automático
        self.session = requests.Session()
        
        # Configuração de retry
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Estado de conexão
        self.is_connected = False
        self.available_models = []
        
        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "average_response_time": 0.0
        }
    
    def initialize(self):
        """Inicializa o cliente Ollama"""
        try:
            self.logger.info("Inicializando OllamaClient...")
            
            # Testa conexão com Ollama
            if self._test_connection():
                self.logger.info(f"Conectado ao Ollama em {self.base_url}")
                
                # Lista modelos disponíveis
                self._load_available_models()
                
                # Verifica se o modelo configurado está disponível
                if self.model not in self.available_models:
                    self.logger.warning(f"Modelo {self.model} não encontrado. Modelos disponíveis: {self.available_models}")
                    
                    # Tenta usar o primeiro modelo disponível
                    if self.available_models:
                        self.model = self.available_models[0]
                        self.logger.info(f"Usando modelo alternativo: {self.model}")
                    else:
                        raise Exception("Nenhum modelo disponível no Ollama")
                
                self.is_connected = True
                self.logger.info("OllamaClient inicializado com sucesso")
                
            else:
                raise Exception("Não foi possível conectar ao Ollama")
                
        except Exception as e:
            self.logger.error(f"Erro ao inicializar OllamaClient: {e}")
            self.is_connected = False
            raise
    
    def _test_connection(self) -> bool:
        """Testa conexão com o servidor Ollama"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.logger.error(f"Erro ao testar conexão: {e}")
            return False
    
    def _load_available_models(self):
        """Carrega lista de modelos disponíveis"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model["name"] for model in data.get("models", [])]
                self.logger.info(f"Modelos disponíveis: {self.available_models}")
            else:
                self.logger.warning(f"Erro ao carregar modelos: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar modelos: {e}")
    
    def send_prompt(self, prompt: str, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Envia prompt para o Ollama e retorna resposta processada
        
        Args:
            prompt: Prompt a ser enviado
            model: Modelo específico (opcional)
            
        Returns:
            Dict com resposta processada ou None em caso de erro
        """
        if not self.is_connected:
            self.logger.error("Cliente não está conectado ao Ollama")
            return None
        
        if not prompt or not isinstance(prompt, str):
            self.logger.error("Prompt inválido")
            return None
        
        start_time = time.time()
        model_to_use = model or self.model
        
        try:
            self.logger.debug(f"Enviando prompt para {model_to_use}: {len(prompt)} caracteres")
            
            # Prepara payload com instruções específicas para JSON
            payload = {
                "model": model_to_use,
                "prompt": f"{prompt}\n\nIMPORTANTE: Responda APENAS com JSON válido, sem texto adicional.",
                "stream": False,
                "format": "json",  # Força formato JSON
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "stop": ["\n\n", "```"]  # Para na primeira quebra dupla ou código
                }
            }
            
            # Envia requisição
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            # Atualiza estatísticas
            self.stats["total_requests"] += 1
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Processa resposta bem-sucedida
                result = self._process_successful_response(response, response_time)
                self.stats["successful_requests"] += 1
                
                # Atualiza tempo médio de resposta
                self._update_average_response_time(response_time)
                
                return result
                
            else:
                # Trata erro HTTP
                self.stats["failed_requests"] += 1
                self.logger.error(f"Erro HTTP {response.status_code}: {response.text}")
                log_error("ollama_client", f"HTTP {response.status_code}", {"response": response.text})
                return None
                
        except requests.exceptions.Timeout:
            self.stats["failed_requests"] += 1
            self.logger.error(f"Timeout ao comunicar com Ollama (>{self.timeout}s)")
            log_error("ollama_client", "timeout", {"timeout": self.timeout})
            return None
            
        except requests.exceptions.ConnectionError:
            self.stats["failed_requests"] += 1
            self.logger.error("Erro de conexão com Ollama")
            log_error("ollama_client", "connection_error", {"url": self.base_url})
            self.is_connected = False
            return None
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            self.logger.error(f"Erro inesperado: {e}")
            log_error("ollama_client", str(e), {"prompt_length": len(prompt)})
            return None
    
    def _process_successful_response(self, response: requests.Response, response_time: float) -> Optional[Dict[str, Any]]:
        """Processa resposta bem-sucedida do Ollama"""
        try:
            data = response.json()
            
            if "response" not in data:
                self.logger.error("Resposta do Ollama não contém campo 'response'")
                return None
            
            raw_response = data["response"]
            
            # Atualiza estatísticas de tokens
            if "eval_count" in data:
                self.stats["total_tokens"] += data["eval_count"]
            
            # Log de debug
            self.logger.debug(f"Resposta recebida em {response_time:.2f}s: {len(raw_response)} caracteres")
            
            # Tenta extrair JSON da resposta
            parsed_response = self._extract_and_validate_json(raw_response)
            
            if parsed_response:
                return parsed_response
            else:
                # Se não conseguir extrair JSON válido, cria resposta de fallback
                return self._create_fallback_response(raw_response)
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON da resposta: {e}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao processar resposta: {e}")
            return None
    
    def _extract_and_validate_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extrai e valida JSON da resposta do modelo"""
        try:
            # Remove espaços em branco e quebras de linha
            text = text.strip()
            
            # Tenta primeiro fazer parse direto (caso seja JSON puro)
            try:
                parsed = json.loads(text)
                if self._validate_json_structure(parsed):
                    self.logger.debug("JSON direto extraído e validado com sucesso")
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Procura por JSON entre chaves
            start = text.find('{')
            if start == -1:
                return None
            
            # Encontra a chave de fechamento correspondente
            brace_count = 0
            end = start
            
            for i in range(start, len(text)):
                if text[i] == '{':
                    brace_count += 1
                elif text[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if brace_count != 0:
                return None
            
            json_str = text[start:end]
            
            # Tenta fazer parse do JSON extraído
            parsed = json.loads(json_str)
            
            if self._validate_json_structure(parsed):
                self.logger.debug("JSON extraído e validado com sucesso")
                return parsed
            else:
                return None
            
        except json.JSONDecodeError:
            return None
        except Exception as e:
            self.logger.debug(f"Erro na extração de JSON: {e}")
            return None
    
    def _validate_json_structure(self, parsed: Any) -> bool:
        """Valida se o JSON tem a estrutura esperada"""
        try:
            # Valida estrutura básica
            if not isinstance(parsed, dict):
                return False
            
            if "internal_monologue" not in parsed or "actions" not in parsed:
                return False
            
            if not isinstance(parsed["actions"], list):
                return False
            
            # Valida cada ação
            for action in parsed["actions"]:
                if not isinstance(action, dict):
                    return False
                if "command" not in action:
                    return False
                # parameter é opcional
            
            return True
            
        except Exception:
            return False
    
    def _create_fallback_response(self, raw_text: str) -> Dict[str, Any]:
        """Cria resposta de fallback quando não consegue extrair JSON válido"""
        # Limita o texto para evitar respostas muito longas
        clean_text = raw_text.strip()
        if len(clean_text) > 500:
            clean_text = clean_text[:497] + "..."
        
        # Remove possíveis marcações de código
        clean_text = clean_text.replace("```json", "").replace("```", "")
        
        fallback_response = {
            "internal_monologue": "O modelo retornou uma resposta em formato não estruturado. Vou tentar interpretar e responder.",
            "actions": [
                {
                    "command": "speak",
                    "parameter": clean_text if clean_text else "Desculpe, tive dificuldades para processar minha resposta."
                }
            ]
        }
        
        self.logger.warning("Criada resposta de fallback para texto não estruturado")
        return fallback_response
    
    def _update_average_response_time(self, response_time: float):
        """Atualiza tempo médio de resposta"""
        if self.stats["successful_requests"] == 1:
            self.stats["average_response_time"] = response_time
        else:
            # Média móvel simples
            current_avg = self.stats["average_response_time"]
            count = self.stats["successful_requests"]
            self.stats["average_response_time"] = (current_avg * (count - 1) + response_time) / count
    
    def get_model_info(self, model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Obtém informações sobre um modelo
        
        Args:
            model_name: Nome do modelo (usa o padrão se não especificado)
            
        Returns:
            Dict com informações do modelo ou None
        """
        if not self.is_connected:
            return None
        
        model_to_check = model_name or self.model
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model_to_check},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"Erro ao obter info do modelo {model_to_check}: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao obter info do modelo: {e}")
            return None
    
    def pull_model(self, model_name: str) -> bool:
        """
        Baixa um modelo do repositório Ollama
        
        Args:
            model_name: Nome do modelo a baixar
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        if not self.is_connected:
            return False
        
        try:
            self.logger.info(f"Iniciando download do modelo {model_name}...")
            
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name},
                timeout=300  # 5 minutos para download
            )
            
            if response.status_code == 200:
                self.logger.info(f"Modelo {model_name} baixado com sucesso")
                self._load_available_models()  # Atualiza lista de modelos
                return True
            else:
                self.logger.error(f"Erro ao baixar modelo {model_name}: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao baixar modelo: {e}")
            return False
    
    def switch_model(self, model_name: str) -> bool:
        """
        Troca o modelo atual
        
        Args:
            model_name: Nome do novo modelo
            
        Returns:
            True se bem-sucedido, False caso contrário
        """
        if model_name not in self.available_models:
            self.logger.warning(f"Modelo {model_name} não está disponível")
            return False
        
        old_model = self.model
        self.model = model_name
        
        self.logger.info(f"Modelo trocado de {old_model} para {model_name}")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do cliente"""
        success_rate = 0.0
        if self.stats["total_requests"] > 0:
            success_rate = (self.stats["successful_requests"] / self.stats["total_requests"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "current_model": self.model,
            "is_connected": self.is_connected,
            "available_models": self.available_models
        }
    
    def health_check(self) -> bool:
        """
        Verifica saúde da conexão
        
        Returns:
            True se saudável, False caso contrário
        """
        if not self.is_connected:
            return False
        
        try:
            # Testa com um prompt simples
            test_prompt = "Responda apenas com: OK"
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": test_prompt,
                    "stream": False,
                    "options": {"num_predict": 10}
                },
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception:
            self.is_connected = False
            return False
    
    def shutdown(self):
        """Encerra o cliente Ollama"""
        if self.session:
            self.session.close()
        
        self.logger.info("OllamaClient encerrado")

if __name__ == "__main__":
    # Teste do OllamaClient
    client = OllamaClient()
    
    try:
        client.initialize()
        
        # Testa envio de prompt
        test_prompt = '''Você é Kairo. Responda com JSON contendo "internal_monologue" e "actions".
        
        Mensagem: Olá!
        
        Exemplo:
        {
          "internal_monologue": "O usuário está cumprimentando",
          "actions": [
            {"command": "speak", "parameter": "Olá! Como vai?"}
          ]
        }'''
        
        print("Enviando prompt de teste...")
        response = client.send_prompt(test_prompt)
        
        if response:
            print("Resposta recebida:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            print("Erro ao receber resposta")
        
        # Mostra estatísticas
        print("\nEstatísticas:")
        stats = client.get_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"Erro no teste: {e}")
    
    finally:
        client.shutdown()

