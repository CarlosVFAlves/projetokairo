"""
cli_executor.py
Executor CLI para o Maestro - Interface de linha de comando
"""

import os
import sys
import time
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime

from executors.base_executor import BaseExecutor, ExecutorCapabilities, ActionResult
from modules.logger import get_logger

class CLIExecutor(BaseExecutor):
    """
    Executor de linha de comando para o Maestro
    Permite interação via terminal com o Kairo
    """
    
    def __init__(self):
        super().__init__("cli_executor")
        self.logger = get_logger('cli_executor')
        
        # Configurações de exibição
        self.colors = {
            "reset": "\033[0m",
            "bold": "\033[1m",
            "dim": "\033[2m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
            "bg_red": "\033[41m",
            "bg_green": "\033[42m",
            "bg_yellow": "\033[43m",
            "bg_blue": "\033[44m",
            "bg_magenta": "\033[45m",
            "bg_cyan": "\033[46m"
        }
        
        # Estado da interface
        self.current_emotion_color = "white"
        self.show_timestamps = True
        self.show_internal_thoughts = True
        self.max_line_length = 80
        
        # Buffer de saída
        self.output_buffer = []
        self.buffer_lock = threading.Lock()
        
        # Capacidades específicas do CLI
        self.capabilities = {
            ExecutorCapabilities.CAN_SPEAK: True,
            ExecutorCapabilities.CAN_DISPLAY_TEXT: True,
            ExecutorCapabilities.CAN_RECEIVE_INPUT: True,
            ExecutorCapabilities.CAN_DISPLAY_EMOTIONS: True,
            ExecutorCapabilities.CAN_CHANGE_COLORS: True,
            ExecutorCapabilities.CAN_SAVE_FILES: True,
            ExecutorCapabilities.CAN_LOAD_FILES: True,
            ExecutorCapabilities.CAN_ACCESS_FILESYSTEM: True,
            "can_clear_screen": True,
            "can_show_ascii_art": True,
            "can_format_text": True
        }
        
        # Mapeamento de emoções para cores
        self.emotion_colors = {
            "joy": "yellow",
            "sadness": "blue",
            "anger": "red",
            "fear": "magenta",
            "surprise": "cyan",
            "interest": "green",
            "neutral": "white"
        }
    
    def initialize(self) -> bool:
        """Inicializa o executor CLI"""
        try:
            self.logger.info("Inicializando CLIExecutor...")
            
            # Verifica se o terminal suporta cores
            if not self._supports_colors():
                self.logger.warning("Terminal não suporta cores - usando modo texto simples")
                self.colors = {key: "" for key in self.colors.keys()}
            
            # Limpa a tela e mostra banner
            self._clear_screen()
            self._show_banner()
            
            self.is_initialized = True
            self.logger.info("CLIExecutor inicializado com sucesso")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar CLIExecutor: {e}")
            return False
    
    def get_available_actions(self) -> List[str]:
        """Retorna ações disponíveis no CLI"""
        return [
            "speak",
            "think",
            "express_emotion",
            "ask_question",
            "request_clarification",
            "show_thought",
            "change_color",
            "clear_screen",
            "show_status",
            "save_conversation",
            "load_conversation",
            "show_help",
            "show_ascii_art",
            "format_text",
            "show_separator",
            "add_goal"
        ]
    
    def get_action_description(self, action: str) -> str:
        """Retorna descrição de uma ação"""
        descriptions = {
            "speak": "Exibe mensagem do Kairo (parameter: {text: string})",
            "think": "Exibe pensamento interno (parameter: string)",
            "express_emotion": "Muda cor baseada na emoção (parameter: {emotion: string, intensity: float})",
            "ask_question": "Exibe pergunta destacada (parameter: {text: string})",
            "request_clarification": "Exibe pedido de esclarecimento (parameter: {text: string})",
            "show_thought": "Exibe pensamento em formato especial (parameter: {text: string})",
            "change_color": "Muda cor do texto (parameter: {color: string})",
            "clear_screen": "Limpa a tela (parameter: none)",
            "show_status": "Exibe status do sistema (parameter: {data: dict})",
            "save_conversation": "Salva conversa em arquivo (parameter: {filename: string})",
            "load_conversation": "Carrega conversa de arquivo (parameter: {filename: string})",
            "show_help": "Exibe ajuda (parameter: none)",
            "show_ascii_art": "Exibe arte ASCII (parameter: {art: string})",
            "format_text": "Formata texto especial (parameter: {text: string, style: string})",
            "show_separator": "Exibe separador visual (parameter: {style: string})",
            "add_goal": "Adiciona um novo objetivo para a IA (uso: /addgoal seu objetivo aqui)"
        }
        
        return descriptions.get(action, f"Ação {action} (descrição não disponível)")
    
    def execute_action(self, action: str, parameters: Any) -> bool:
        """Executa uma ação no CLI"""
        try:
            if not self.validate_action(action, parameters):
                return False
            
            success = False
            
            if action == "speak":
                success = self._action_speak(parameters)
            elif action == "think":
                success = self._action_think(parameters)
            elif action == "express_emotion":
                success = self._action_express_emotion(parameters)
            elif action == "ask_question":
                success = self._action_ask_question(parameters)
            elif action == "request_clarification":
                success = self._action_request_clarification(parameters)
            elif action == "show_thought":
                success = self._action_show_thought(parameters)
            elif action == "change_color":
                success = self._action_change_color(parameters)
            elif action == "clear_screen":
                success = self._action_clear_screen(parameters)
            elif action == "show_status":
                success = self._action_show_status(parameters)
            elif action == "save_conversation":
                success = self._action_save_conversation(parameters)
            elif action == "load_conversation":
                success = self._action_load_conversation(parameters)
            elif action == "show_help":
                success = self._action_show_help(parameters)
            elif action == "show_ascii_art":
                success = self._action_show_ascii_art(parameters)
            elif action == "format_text":
                success = self._action_format_text(parameters)
            elif action == "show_separator":
                success = self._action_show_separator(parameters)
            else:
                self.logger.warning(f"Ação desconhecida: {action}")
                success = False
            
            self._update_stats(success)
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação {action}: {e}")
            self._update_stats(False)
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Retorna capacidades do executor CLI"""
        return self.capabilities.copy()
    
    def shutdown(self):
        """Encerra o executor CLI"""
        try:
            self._print_colored("\n" + "="*50, "dim")
            self._print_colored("Kairo CLI encerrado. Até logo!", "green")
            self._print_colored("="*50, "dim")
            
            self.is_initialized = False
            self.logger.info("CLIExecutor encerrado")
            
        except Exception as e:
            self.logger.error(f"Erro ao encerrar CLIExecutor: {e}")
    
    # Implementação das ações específicas
    
    def _action_speak(self, parameters: Any) -> bool:
        """Ação de fala do Kairo"""
        try:
            if isinstance(parameters, dict):
                text = parameters.get("text", str(parameters))
            else:
                text = str(parameters)
            
            if not text:
                return False
            
            timestamp = self._get_timestamp() if self.show_timestamps else ""
            
            # Formata a mensagem
            self._print_colored(f"\n{timestamp}", "dim")
            self._print_colored("🤖 Kairo: ", "bold")
            self._print_wrapped(text, self.current_emotion_color)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_speak: {e}")
            return False
    
    def _action_think(self, parameters: Any) -> bool:
        """Ação de pensamento interno"""
        try:
            if not self.show_internal_thoughts:
                return True
            
            thought = str(parameters) if parameters else ""
            
            if thought:
                timestamp = self._get_timestamp() if self.show_timestamps else ""
                
                self._print_colored(f"\n{timestamp}", "dim")
                self._print_colored("💭 [Pensamento]: ", "dim")
                self._print_wrapped(thought, "dim")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_think: {e}")
            return False
    
    def _action_express_emotion(self, parameters: Any) -> bool:
        """Ação de expressão emocional"""
        try:
            if not isinstance(parameters, dict):
                return False
            
            emotion = parameters.get("emotion", "neutral")
            intensity = parameters.get("intensity", 5.0)
            
            # Muda cor baseada na emoção
            new_color = self.emotion_colors.get(emotion, "white")
            self.current_emotion_color = new_color
            
            # Exibe indicador visual da emoção
            emotion_indicator = self._get_emotion_indicator(emotion, intensity)
            self._print_colored(f"\n{emotion_indicator}", new_color)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_express_emotion: {e}")
            return False
    
    def _action_ask_question(self, parameters: Any) -> bool:
        """Ação de pergunta"""
        try:
            if isinstance(parameters, dict):
                text = parameters.get("text", str(parameters))
            else:
                text = str(parameters)
            
            if not text:
                return False
            
            timestamp = self._get_timestamp() if self.show_timestamps else ""
            
            self._print_colored(f"\n{timestamp}", "dim")
            self._print_colored("❓ Kairo pergunta: ", "yellow")
            self._print_wrapped(text, "yellow")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_ask_question: {e}")
            return False
    
    def _action_request_clarification(self, parameters: Any) -> bool:
        """Ação de pedido de esclarecimento"""
        try:
            if isinstance(parameters, dict):
                text = parameters.get("text", str(parameters))
            else:
                text = str(parameters)
            
            if not text:
                return False
            
            timestamp = self._get_timestamp() if self.show_timestamps else ""
            
            self._print_colored(f"\n{timestamp}", "dim")
            self._print_colored("🤔 Kairo precisa esclarecer: ", "cyan")
            self._print_wrapped(text, "cyan")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_request_clarification: {e}")
            return False
    
    def _action_show_thought(self, parameters: Any) -> bool:
        """Ação de exibição de pensamento especial"""
        try:
            if isinstance(parameters, dict):
                text = parameters.get("text", str(parameters))
            else:
                text = str(parameters)
            
            if not text:
                return False
            
            # Caixa de pensamento
            self._print_colored("\n┌" + "─" * (self.max_line_length - 2) + "┐", "dim")
            self._print_colored("│ 💭 Pensamento:", "dim")
            
            # Quebra o texto em linhas
            words = text.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= self.max_line_length - 6:
                    current_line += " " + word if current_line else word
                else:
                    self._print_colored(f"│ {current_line:<{self.max_line_length - 4}} │", "dim")
                    current_line = word
            
            if current_line:
                self._print_colored(f"│ {current_line:<{self.max_line_length - 4}} │", "dim")
            
            self._print_colored("└" + "─" * (self.max_line_length - 2) + "┘", "dim")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_show_thought: {e}")
            return False
    
    def _action_change_color(self, parameters: Any) -> bool:
        """Ação de mudança de cor"""
        try:
            if isinstance(parameters, dict):
                color = parameters.get("color", "white")
            else:
                color = str(parameters)
            
            if color in self.colors:
                self.current_emotion_color = color
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro em _action_change_color: {e}")
            return False
    
    def _action_clear_screen(self, parameters: Any) -> bool:
        """Ação de limpeza de tela"""
        try:
            self._clear_screen()
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_clear_screen: {e}")
            return False
    
    def _action_show_status(self, parameters: Any) -> bool:
        """Ação de exibição de status"""
        try:
            if isinstance(parameters, dict):
                data = parameters.get("data", {})
            else:
                data = {}
            
            self._print_colored("\n📊 Status do Sistema:", "bold")
            self._print_colored("-" * 30, "dim")
            
            for key, value in data.items():
                self._print_colored(f"{key}: {value}", "white")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_show_status: {e}")
            return False
    
    def _action_save_conversation(self, parameters: Any) -> bool:
        """Ação de salvamento de conversa"""
        try:
            if isinstance(parameters, dict):
                filename = parameters.get("filename", f"conversa_{int(time.time())}.txt")
            else:
                filename = str(parameters)
            
            # Salva buffer de saída
            with self.buffer_lock:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self.output_buffer))
            
            self._print_colored(f"\n💾 Conversa salva em: {filename}", "green")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_save_conversation: {e}")
            return False
    
    def _action_load_conversation(self, parameters: Any) -> bool:
        """Ação de carregamento de conversa"""
        try:
            if isinstance(parameters, dict):
                filename = parameters.get("filename", "")
            else:
                filename = str(parameters)
            
            if not filename or not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._print_colored(f"\n📂 Conversa carregada de: {filename}", "green")
            self._print_colored("-" * 50, "dim")
            print(content)
            self._print_colored("-" * 50, "dim")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_load_conversation: {e}")
            return False
    
    def _action_show_help(self, parameters: Any) -> bool:
        """Ação de exibição de ajuda"""
        try:
            help_text = """
🤖 Kairo CLI - Comandos Disponíveis:

Comandos do usuário:
  /help     - Mostra esta ajuda
  /status   - Mostra status do sistema
  /clear    - Limpa a tela
  /addgoal  - Adiciona um novo objetivo para a IA
  /save     - Salva conversa
  /load     - Carrega conversa
  /quit     - Encerra o programa

Ações do Kairo:
  speak     - Falar com o usuário
  think     - Pensamento interno
  express_emotion - Expressar emoção
  ask_question - Fazer pergunta
  
Configurações:
  - Timestamps: {timestamps}
  - Pensamentos internos: {thoughts}
  - Cor atual: {color}
            """.format(
                timestamps="Ativados" if self.show_timestamps else "Desativados",
                thoughts="Ativados" if self.show_internal_thoughts else "Desativados",
                color=self.current_emotion_color
            )
            
            self._print_colored(help_text, "cyan")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_show_help: {e}")
            return False
    
    def _action_show_ascii_art(self, parameters: Any) -> bool:
        """Ação de exibição de arte ASCII"""
        try:
            if isinstance(parameters, dict):
                art = parameters.get("art", "")
            else:
                art = str(parameters)
            
            if art:
                self._print_colored(f"\n{art}", "cyan")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_show_ascii_art: {e}")
            return False
    
    def _action_format_text(self, parameters: Any) -> bool:
        """Ação de formatação de texto"""
        try:
            if not isinstance(parameters, dict):
                return False
            
            text = parameters.get("text", "")
            style = parameters.get("style", "normal")
            
            if style == "bold":
                self._print_colored(text, "bold")
            elif style == "dim":
                self._print_colored(text, "dim")
            elif style == "highlight":
                self._print_colored(text, "bg_yellow")
            else:
                self._print_colored(text, "white")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_format_text: {e}")
            return False
    
    def _action_show_separator(self, parameters: Any) -> bool:
        """Ação de exibição de separador"""
        try:
            if isinstance(parameters, dict):
                style = parameters.get("style", "line")
            else:
                style = str(parameters)
            
            if style == "line":
                self._print_colored("-" * self.max_line_length, "dim")
            elif style == "double":
                self._print_colored("=" * self.max_line_length, "dim")
            elif style == "dots":
                self._print_colored("." * self.max_line_length, "dim")
            else:
                self._print_colored("-" * self.max_line_length, "dim")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em _action_show_separator: {e}")
            return False
    
    # Métodos auxiliares
    
    def _supports_colors(self) -> bool:
        """Verifica se o terminal suporta cores"""
        return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def _clear_screen(self):
        """Limpa a tela"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _show_banner(self):
        """Exibe banner inicial"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                            🤖 KAIRO CLI v1.0                                ║
║                                                                              ║
║                    Sistema Maestro - Interface de Linha de Comando          ║
║                                                                              ║
║                         Digite /help para ver comandos                      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        self._print_colored(banner, "cyan")
        self._print_colored("Kairo está inicializando...\n", "green")
    
    def _print_colored(self, text: str, color: str):
        """Imprime texto colorido"""
        color_code = self.colors.get(color, "")
        reset_code = self.colors.get("reset", "")
        
        output = f"{color_code}{text}{reset_code}"
        print(output)
        
        # Adiciona ao buffer
        with self.buffer_lock:
            self.output_buffer.append(text)
            
            # Limita tamanho do buffer
            if len(self.output_buffer) > 1000:
                self.output_buffer = self.output_buffer[-800:]
    
    def _print_wrapped(self, text: str, color: str):
        """Imprime texto com quebra de linha"""
        words = text.split()
        current_line = ""
        
        for word in words:
            if len(current_line + " " + word) <= self.max_line_length:
                current_line += " " + word if current_line else word
            else:
                if current_line:
                    self._print_colored(current_line, color)
                current_line = word
        
        if current_line:
            self._print_colored(current_line, color)
    
    def _get_timestamp(self) -> str:
        """Obtém timestamp formatado"""
        return f"[{datetime.now().strftime('%H:%M:%S')}] "
    
    def _get_emotion_indicator(self, emotion: str, intensity: float) -> str:
        """Obtém indicador visual da emoção"""
        indicators = {
            "joy": "😊",
            "sadness": "😢",
            "anger": "😠",
            "fear": "😰",
            "surprise": "😲",
            "interest": "🤔",
            "neutral": "😐"
        }
        
        emoji = indicators.get(emotion, "😐")
        intensity_bar = "█" * int(intensity / 2)  # Barra de 0-5 caracteres
        
        return f"{emoji} {emotion.capitalize()} {intensity_bar} ({intensity:.1f}/10)"

if __name__ == "__main__":
    # Teste do CLIExecutor
    cli = CLIExecutor()
    
    if cli.initialize():
        print("\nTestando ações do CLIExecutor:")
        
        # Testa fala
        cli.execute_action("speak", {"text": "Olá! Eu sou o Kairo!"})
        
        # Testa pensamento
        cli.execute_action("think", "Hmm, o usuário parece interessado...")
        
        # Testa emoção
        cli.execute_action("express_emotion", {"emotion": "joy", "intensity": 7.5})
        
        # Testa pergunta
        cli.execute_action("ask_question", {"text": "Como você está se sentindo hoje?"})
        
        # Testa separador
        cli.execute_action("show_separator", {"style": "double"})
        
        # Testa status
        cli.execute_action("show_status", {"data": {"Ações executadas": 5, "Status": "Funcionando"}})
        
        print(f"\nEstatísticas: {cli.get_stats()}")
        print(f"Ações disponíveis: {len(cli.get_available_actions())}")
        
        cli.shutdown()
    else:
        print("Erro ao inicializar CLIExecutor")

