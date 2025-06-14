"""
base_executor.py
Interface base para todos os executores do Maestro
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional

class BaseExecutor(ABC):
    """
    Interface base que todos os executores devem implementar
    Define o contrato entre o Maestro (cérebro) e os executores (corpos)
    """
    
    def __init__(self, executor_id: str):
        self.executor_id = executor_id
        self.is_initialized = False
        self.capabilities = {}
        self.stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0
        }
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Inicializa o executor
        
        Returns:
            True se inicializado com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_available_actions(self) -> List[str]:
        """
        Retorna lista de ações que este executor pode executar
        
        Returns:
            Lista de nomes de ações disponíveis
        """
        pass
    
    @abstractmethod
    def get_action_description(self, action: str) -> str:
        """
        Retorna descrição de uma ação específica
        
        Args:
            action: Nome da ação
            
        Returns:
            Descrição da ação e seus parâmetros
        """
        pass
    
    @abstractmethod
    def execute_action(self, action: str, parameters: Any) -> bool:
        """
        Executa uma ação específica
        
        Args:
            action: Nome da ação a executar
            parameters: Parâmetros da ação
            
        Returns:
            True se executada com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Retorna capacidades específicas deste executor
        
        Returns:
            Dict com capacidades e limitações
        """
        pass
    
    @abstractmethod
    def shutdown(self):
        """
        Encerra o executor e libera recursos
        """
        pass
    
    # Métodos auxiliares comuns
    
    def get_executor_info(self) -> Dict[str, Any]:
        """
        Retorna informações gerais do executor
        
        Returns:
            Dict com informações do executor
        """
        return {
            "executor_id": self.executor_id,
            "is_initialized": self.is_initialized,
            "available_actions": self.get_available_actions(),
            "capabilities": self.get_capabilities(),
            "stats": self.get_stats()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do executor
        
        Returns:
            Dict com estatísticas de uso
        """
        success_rate = 0.0
        if self.stats["total_actions"] > 0:
            success_rate = (self.stats["successful_actions"] / self.stats["total_actions"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate
        }
    
    def _update_stats(self, success: bool):
        """
        Atualiza estatísticas de execução
        
        Args:
            success: Se a ação foi bem-sucedida
        """
        self.stats["total_actions"] += 1
        if success:
            self.stats["successful_actions"] += 1
        else:
            self.stats["failed_actions"] += 1
    
    def validate_action(self, action: str, parameters: Any) -> bool:
        """
        Valida se uma ação pode ser executada
        
        Args:
            action: Nome da ação
            parameters: Parâmetros da ação
            
        Returns:
            True se válida, False caso contrário
        """
        if not self.is_initialized:
            return False
        
        if action not in self.get_available_actions():
            return False
        
        return True
    
    def format_action_list(self) -> str:
        """
        Formata lista de ações disponíveis para exibição
        
        Returns:
            String formatada com ações e descrições
        """
        actions = self.get_available_actions()
        formatted_lines = []
        
        for action in actions:
            description = self.get_action_description(action)
            formatted_lines.append(f"- {action}: {description}")
        
        return "\n".join(formatted_lines)

class ExecutorCapabilities:
    """
    Classe auxiliar para definir capacidades padrão dos executores
    """
    
    # Capacidades de comunicação
    CAN_SPEAK = "can_speak"
    CAN_LISTEN = "can_listen"
    CAN_DISPLAY_TEXT = "can_display_text"
    CAN_DISPLAY_IMAGES = "can_display_images"
    
    # Capacidades visuais
    CAN_CHANGE_COLORS = "can_change_colors"
    CAN_SHOW_ANIMATIONS = "can_show_animations"
    CAN_DISPLAY_EMOTIONS = "can_display_emotions"
    
    # Capacidades de interação
    CAN_RECEIVE_INPUT = "can_receive_input"
    CAN_SEND_NOTIFICATIONS = "can_send_notifications"
    CAN_SAVE_FILES = "can_save_files"
    CAN_LOAD_FILES = "can_load_files"
    
    # Capacidades de rede
    CAN_CONNECT_INTERNET = "can_connect_internet"
    CAN_SEND_EMAILS = "can_send_emails"
    CAN_USE_APIS = "can_use_apis"
    
    # Capacidades de sistema
    CAN_EXECUTE_COMMANDS = "can_execute_commands"
    CAN_ACCESS_FILESYSTEM = "can_access_filesystem"
    CAN_CONTROL_HARDWARE = "can_control_hardware"
    
    @classmethod
    def get_all_capabilities(cls) -> List[str]:
        """Retorna lista de todas as capacidades disponíveis"""
        return [
            cls.CAN_SPEAK, cls.CAN_LISTEN, cls.CAN_DISPLAY_TEXT, cls.CAN_DISPLAY_IMAGES,
            cls.CAN_CHANGE_COLORS, cls.CAN_SHOW_ANIMATIONS, cls.CAN_DISPLAY_EMOTIONS,
            cls.CAN_RECEIVE_INPUT, cls.CAN_SEND_NOTIFICATIONS, cls.CAN_SAVE_FILES, cls.CAN_LOAD_FILES,
            cls.CAN_CONNECT_INTERNET, cls.CAN_SEND_EMAILS, cls.CAN_USE_APIS,
            cls.CAN_EXECUTE_COMMANDS, cls.CAN_ACCESS_FILESYSTEM, cls.CAN_CONTROL_HARDWARE
        ]
    
    @classmethod
    def get_basic_capabilities(cls) -> List[str]:
        """Retorna capacidades básicas que a maioria dos executores deve ter"""
        return [
            cls.CAN_SPEAK,
            cls.CAN_DISPLAY_TEXT,
            cls.CAN_RECEIVE_INPUT,
            cls.CAN_DISPLAY_EMOTIONS
        ]

class ActionResult:
    """
    Classe para representar resultado de uma ação
    """
    
    def __init__(self, success: bool, message: str = "", data: Any = None):
        self.success = success
        self.message = message
        self.data = data
        self.timestamp = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte resultado para dicionário"""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def success(cls, message: str = "Ação executada com sucesso", data: Any = None):
        """Cria resultado de sucesso"""
        return cls(True, message, data)
    
    @classmethod
    def failure(cls, message: str = "Falha ao executar ação", data: Any = None):
        """Cria resultado de falha"""
        return cls(False, message, data)

if __name__ == "__main__":
    # Exemplo de uso da interface base
    print("BaseExecutor - Interface para executores do Maestro")
    print("\nCapacidades disponíveis:")
    for capability in ExecutorCapabilities.get_all_capabilities():
        print(f"  - {capability}")
    
    print("\nCapacidades básicas:")
    for capability in ExecutorCapabilities.get_basic_capabilities():
        print(f"  - {capability}")
    
    print("\nEsta interface define o contrato que todos os executores devem seguir:")
    print("- initialize(): Inicializa o executor")
    print("- get_available_actions(): Lista ações disponíveis")
    print("- execute_action(): Executa uma ação específica")
    print("- get_capabilities(): Retorna capacidades do executor")
    print("- shutdown(): Encerra o executor")
    
    print("\nExemplos de executores:")
    print("- CLIExecutor: Interface de linha de comando")
    print("- WebExecutor: Interface web com Flask")
    print("- GameExecutor: Interface para jogos via WebSocket")
    print("- RobotExecutor: Interface para controle de robôs")
    print("- VRExecutor: Interface para realidade virtual")

