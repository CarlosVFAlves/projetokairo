"""
main.py
Ponto de entrada principal do Sistema Maestro
"""

import sys
import time
import signal
import threading
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from config import OLLAMA_CONFIG, PERSONALITY_CONFIG, EMOTION_CONFIG, MEMORY_CONFIG, IDLE_CONFIG
from modules.logger import get_logger, log_system_event
from modules.state_manager import StateManager
from modules.emotion_engine import EmotionEngine
from modules.personality_core import PersonalityCore
from modules.prompt_engine import PromptEngine
from modules.openai_client import OpenAIClient
from modules.action_executor import ActionExecutor
from modules.idle_processor import IdleProcessor
from executors.cli_executor import CLIExecutor

class MaestroSystem:
    """
    Sistema principal do Maestro
    Orquestra todos os módulos cognitivos e executores
    """
    
    def __init__(self):
        self.logger = get_logger('maestro_system')
        
        # Módulos cognitivos
        self.state_manager = None
        self.emotion_engine = None
        self.personality_core = None
        self.prompt_engine = None
        self.llm_client = None
        self.action_executor = None
        self.idle_processor = None
        
        # Executor atual
        self.executor = None
        
        # Estado do sistema
        self.running = False
        self.initialization_complete = False
        
        # Thread de entrada do usuário
        self.input_thread = None
    
    def initialize(self, executor_type: str = "cli") -> bool:
        """
        Inicializa o sistema Maestro
        
        Args:
            executor_type: Tipo de executor (cli, web, etc.)
            
        Returns:
            True se inicializado com sucesso
        """
        try:
            self.logger.info("Inicializando Sistema Maestro...")
            log_system_event("maestro_startup", "Iniciando sistema")
            
            # 1. Inicializa módulos cognitivos na ordem correta
            self.logger.info("Inicializando módulos cognitivos...")
            
            # State Manager (base para todos os outros)
            self.state_manager = StateManager()
            if not self._safe_initialize(self.state_manager, "StateManager"):
                return False
            
            # Emotion Engine
            self.emotion_engine = EmotionEngine(self.state_manager)
            if not self._safe_initialize(self.emotion_engine, "EmotionEngine"):
                return False
            
            # Personality Core
            self.personality_core = PersonalityCore(self.state_manager, self.emotion_engine)
            if not self._safe_initialize(self.personality_core, "PersonalityCore"):
                return False
            
            # Prompt Engine
            self.prompt_engine = PromptEngine(self.state_manager, self.emotion_engine, self.personality_core)
            if not self._safe_initialize(self.prompt_engine, "PromptEngine"):
                return False
            
            # LLM Client (OpenAI)
            self.llm_client = OpenAIClient()
            if not self._safe_initialize(self.llm_client, "OpenAIClient"):
                return False
            
            # 2. Inicializa executor
            self.logger.info(f"Inicializando executor: {executor_type}")
            
            if executor_type == "cli":
                self.executor = CLIExecutor()
            else:
                raise Exception(f"Tipo de executor desconhecido: {executor_type}")
            
            if not self._safe_initialize(self.executor, f"{executor_type.upper()}Executor"):
                return False
            
            # 3. Inicializa Action Executor (precisa do executor)
            self.action_executor = ActionExecutor(self.executor, self.state_manager)
            if not self._safe_initialize(self.action_executor, "ActionExecutor"):
                return False
            
            # 4. Inicializa Idle Processor (precisa de todos os outros)
            self.idle_processor = IdleProcessor(
                self.state_manager,
                self.emotion_engine,
                self.personality_core,
                self.prompt_engine,
                self.llm_client,
                self.action_executor
            )
            if not self._safe_initialize(self.idle_processor, "IdleProcessor"):
                return False
            
            # 5. Configuração final
            self._setup_signal_handlers()
            
            self.initialization_complete = True
            self.logger.info("Sistema Maestro inicializado com sucesso!")
            
            # Mensagem de boas-vindas
            self._show_welcome_message()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro crítico na inicialização: {e}")
            return False
    
    def _safe_initialize(self, module, module_name: str) -> bool:
        """Inicializa um módulo com tratamento de erro"""
        try:
            module.initialize()
            self.logger.info(f"{module_name} inicializado com sucesso")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao inicializar {module_name}: {e}")
            return False
    
    def _setup_signal_handlers(self):
        """Configura handlers para sinais do sistema"""
        def signal_handler(signum, frame):
            self.logger.info(f"Sinal {signum} recebido - encerrando sistema...")
            self.shutdown()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def _show_welcome_message(self):
        """Exibe mensagem de boas-vindas"""
        try:
            # Obtém informações do estado atual
            kairo_age = self.state_manager.get_kairo_age_hours()
            interaction_count = self.state_manager.get_interaction_count()
            
            welcome_plan = {
                "internal_monologue": f"Sistema inicializado! Tenho {kairo_age:.1f} horas de vida e {interaction_count} interações registradas.",
                "actions": [
                    {"command": "speak", "parameter": {"text": f"Olá! Eu sou o Kairo. Tenho {kairo_age:.1f} horas de vida e já tive {interaction_count} interações. Como posso ajudá-lo hoje?"}},
                    {"command": "express_emotion", "parameter": {"emotion": "interest", "intensity": 6.0}},
                    {"command": "show_separator", "parameter": {"style": "line"}}
                ]
            }
            
            self.action_executor.execute_plan(welcome_plan)
            
        except Exception as e:
            self.logger.error(f"Erro ao exibir mensagem de boas-vindas: {e}")
    
    def run(self):
        """Executa o loop principal do sistema"""
        if not self.initialization_complete:
            self.logger.error("Sistema não foi inicializado corretamente")
            return
        
        try:
            self.running = True
            self.logger.info("Iniciando loop principal do Maestro")
            
            # Inicia thread de entrada do usuário
            self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
            self.input_thread.start()
            
            # Loop principal
            while self.running:
                try:
                    time.sleep(1)  # Evita uso excessivo de CPU
                    
                    # Aqui poderiam ser adicionadas outras tarefas periódicas
                    
                except KeyboardInterrupt:
                    self.logger.info("Interrupção do usuário detectada")
                    break
                except Exception as e:
                    self.logger.error(f"Erro no loop principal: {e}")
            
        except Exception as e:
            self.logger.error(f"Erro crítico no loop principal: {e}")
        finally:
            self.shutdown()
    
    def _input_loop(self):
        """Loop de entrada do usuário"""
        try:
            while self.running:
                try:
                    # Lê entrada do usuário
                    user_input = input("\n👤 Você: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Processa comandos especiais
                    if user_input.startswith('/'):
                        self._process_command(user_input)
                        continue
                    
                    # Processa mensagem normal
                    self._process_user_message(user_input)
                    
                except EOFError:
                    # Ctrl+D pressionado
                    self.logger.info("EOF detectado - encerrando...")
                    self.running = False
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressionado
                    self.logger.info("Interrupção detectada - encerrando...")
                    self.running = False
                    break
                except Exception as e:
                    self.logger.error(f"Erro no loop de entrada: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro crítico no loop de entrada: {e}")
    
    def _process_command(self, command: str):
        """Processa comandos especiais do usuário"""
        try:
            cmd = command.lower().strip()
            
            if cmd == '/help':
                self.executor.execute_action("show_help", {})
            elif cmd == '/status':
                self._show_system_status()
            elif cmd == '/clear':
                self.executor.execute_action("clear_screen", {})
            elif cmd == '/save':
                filename = f"conversa_{int(time.time())}.txt"
                self.executor.execute_action("save_conversation", {"filename": filename})
            elif cmd in ['/quit', '/exit', '/bye']:
                self.executor.execute_action("speak", {"text": "Até logo! Foi um prazer conversar com você."})
                self.running = False
            else:
                self.executor.execute_action("speak", {"text": f"Comando desconhecido: {command}. Digite /help para ver comandos disponíveis."})
                
        except Exception as e:
            self.logger.error(f"Erro ao processar comando {command}: {e}")
    
    def _process_user_message(self, message: str):
        """Processa a mensagem do usuário usando um fluxo de streaming."""
        try:
            self.idle_processor.update_interaction_time()
            user_id = self.state_manager.get_current_user_id()
            self.state_manager.add_memory(f"Usuário disse: {message}", "user_message", user_id)
            self.emotion_engine.analyze_text(message, "user")
            self.personality_core.analyze_interaction(message, "user_message")

            prompt = self.prompt_engine.generate_prompt(message, "conversation")
            stream = self.llm_client.stream_prompt(prompt)

            if not stream:
                self.logger.error("Não foi possível iniciar o stream com o LLM.")
                self._handle_llm_failure()
                return

            full_response_for_memory = []
            for chunk in stream:
                if "error" in chunk:
                    self.logger.error(f"Erro no stream do LLM: {chunk.get('details')}")
                    self._handle_llm_failure()
                    break

                if "internal_monologue" in chunk:
                    self.action_executor.execute_plan(chunk)

                if "command" in chunk:
                    plan = {"actions": [chunk]}
                    self.action_executor.execute_plan(plan)

                    if chunk.get("command") == "speak":
                        param = chunk.get("parameter")
                        if isinstance(param, dict):
                            text = param.get("text", "")
                        else:
                            text = str(param)

                        if text:
                            full_response_for_memory.append(text)

            if full_response_for_memory:
                response_text = " ".join(full_response_for_memory)
                self.state_manager.add_memory(f"Kairo respondeu: {response_text}", "kairo_response", user_id)

        except Exception as e:
            self.logger.error(f"Erro ao processar mensagem do usuário: {e}", exc_info=True)
            self._handle_processing_error(str(e))

    def _show_system_status(self):
        """Exibe status detalhado do sistema"""
        try:
            # Coleta informações de todos os módulos
            status_data = {
                "Sistema": "Maestro v1.0",
                "Status": "Funcionando" if self.running else "Parado",
                "Idade do Kairo": f"{self.state_manager.get_kairo_age_hours():.1f}h",
                "Interações": self.state_manager.get_interaction_count(),
                "Memórias": len(self.state_manager.kairo_state["memories"]),
                "LLM": f"OpenAI ({'Conectado' if self.llm_client.is_connected else 'Desconectado'})",
                "Executor": self.executor.executor_id,
                "Ações executadas": self.action_executor.stats["total_actions"]
            }
            
            # Adiciona informações emocionais
            dominant_emotion, intensity = self.emotion_engine.get_dominant_emotion()
            status_data["Emoção dominante"] = f"{dominant_emotion} ({intensity:.1f})"
            
            # Adiciona traço de personalidade mais desenvolvido
            learning_progress = self.personality_core.get_learning_progress()
            most_developed = learning_progress.get("most_developed_trait", "Nenhum")
            status_data["Traço mais desenvolvido"] = most_developed
            
            self.executor.execute_action("show_status", {"data": status_data})
            
        except Exception as e:
            self.logger.error(f"Erro ao exibir status: {e}")
    
    def _handle_execution_failure(self):
        """Trata falha na execução de ações"""
        fallback_plan = {
            "internal_monologue": "Houve um problema ao executar minha resposta.",
            "actions": [
                {"command": "speak", "parameter": {"text": "Desculpe, tive um problema interno. Pode repetir sua mensagem?"}}
            ]
        }
        
        self.action_executor.execute_plan(fallback_plan)
    
    def _handle_llm_failure(self):
        """Trata falha na comunicação com o LLM"""
        fallback_plan = {
            "internal_monologue": "Não consegui me comunicar com meu sistema de processamento.",
            "actions": [
                {"command": "speak", "parameter": {"text": "Desculpe, estou com problemas de comunicação interna. Tente novamente em alguns momentos."}}
            ]
        }
        
        self.action_executor.execute_plan(fallback_plan)
    
    def _handle_processing_error(self, error_msg: str):
        """Trata erro geral de processamento"""
        fallback_plan = {
            "internal_monologue": f"Erro no processamento: {error_msg}",
            "actions": [
                {"command": "speak", "parameter": {"text": "Ops, algo deu errado no meu processamento. Pode tentar de novo?"}}
            ]
        }
        
        self.action_executor.execute_plan(fallback_plan)
    
    def shutdown(self):
        """Encerra o sistema Maestro"""
        try:
            if not self.running:
                return
            
            self.logger.info("Encerrando Sistema Maestro...")
            self.running = False
            
            # Encerra módulos na ordem inversa
            modules_to_shutdown = [
                (self.idle_processor, "IdleProcessor"),
                (self.action_executor, "ActionExecutor"),
                (self.executor, "Executor"),
                (self.llm_client, "OpenAIClient"),
                (self.prompt_engine, "PromptEngine"),
                (self.personality_core, "PersonalityCore"),
                (self.emotion_engine, "EmotionEngine"),
                (self.state_manager, "StateManager")
            ]
            
            for module, name in modules_to_shutdown:
                if module:
                    try:
                        module.shutdown()
                        self.logger.info(f"{name} encerrado")
                    except Exception as e:
                        self.logger.error(f"Erro ao encerrar {name}: {e}")
            
            log_system_event("maestro_shutdown", "Sistema encerrado")
            self.logger.info("Sistema Maestro encerrado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao encerrar sistema: {e}")

def main():
    """Função principal"""
    try:
        # Cria e inicializa sistema
        maestro = MaestroSystem()
        
        if maestro.initialize("cli"):
            # Executa sistema
            maestro.run()
        else:
            print("Erro: Falha na inicialização do sistema Maestro")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Erro crítico: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
