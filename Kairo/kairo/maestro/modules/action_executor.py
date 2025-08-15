"""
action_executor.py
Executor de ações do Maestro
"""

import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from modules.logger import get_logger, log_decision, log_error

class ActionExecutor:
    """
    Executor de ações do Maestro
    Traduz comandos cognitivos abstratos em ações específicas do executor
    """
    
    def __init__(self, executor, state_manager):
        self.logger = get_logger('action_executor')
        self.executor = executor  # Executor específico (CLI, Web, Game, etc.)
        self.state_manager = state_manager
        
        # Mapeamento de comandos abstratos para métodos
        self.command_handlers = {
            # Comunicação
            "speak": self._handle_speak,
            "think": self._handle_think,
            "express_emotion": self._handle_express_emotion,
            
            # Estado interno
            "adjust_emotion": self._handle_adjust_emotion,
            "update_personality": self._handle_update_personality,
            
            # Interação com usuário
            "ask_question": self._handle_ask_question,
            "request_clarification": self._handle_request_clarification,
            
            # Memória e aprendizado
            "add_user_fact": self._handle_add_user_fact,
            "update_user_profile": self._handle_update_user_profile,
            "remember_important": self._handle_remember_important,
            
            # Ações específicas do executor
            "executor_action": self._handle_executor_action
        }
        
        # Estatísticas
        self.stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "commands_by_type": {}
        }
    
    def initialize(self):
        """Inicializa o executor de ações"""
        try:
            self.logger.info("Inicializando ActionExecutor...")
            
            # Verifica se o executor tem os métodos necessários
            required_methods = ["get_available_actions", "execute_action"]
            for method in required_methods:
                if not hasattr(self.executor, method):
                    raise Exception(f"Executor não implementa método obrigatório: {method}")
            
            self.logger.info("ActionExecutor inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar ActionExecutor: {e}")
            raise
    
    def execute_plan(self, plan: Dict[str, Any]) -> bool:
        """
        Executa um plano de ações do Maestro
        
        Args:
            plan: Plano contendo internal_monologue e actions
            
        Returns:
            True se executado com sucesso, False caso contrário
        """
        try:
            if not isinstance(plan, dict):
                self.logger.error(f"Plano inválido: {type(plan)}")
                return False
            
            # Log do monólogo interno
            if "internal_monologue" in plan:
                self._log_internal_monologue(plan["internal_monologue"])
            
            # Executa ações
            if "actions" in plan and isinstance(plan["actions"], list):
                success = True
                
                for action in plan["actions"]:
                    if not self.execute_action(action):
                        success = False
                        # Continua executando outras ações mesmo se uma falhar
                
                return success
            else:
                self.logger.warning("Plano não contém ações válidas")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao executar plano: {e}")
            log_error("action_executor", str(e), {"plan": plan})
            return False
    
    def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Executa uma ação específica
        
        Args:
            action: Dict com command e parameter
            
        Returns:
            True se executada com sucesso, False caso contrário
        """
        try:
            if not isinstance(action, dict):
                self.logger.error(f"Ação inválida: {type(action)}")
                return False
            
            command = action.get("command")
            parameter = action.get("parameter")
            
            if not command:
                self.logger.error("Ação sem comando")
                return False
            
            # Atualiza estatísticas
            self.stats["total_actions"] += 1
            self.stats["commands_by_type"][command] = self.stats["commands_by_type"].get(command, 0) + 1
            
            # Log da decisão
            log_decision("action_execution", command, f"parameter: {parameter}")
            
            # Executa o comando
            if command in self.command_handlers:
                success = self.command_handlers[command](parameter)
            else:
                # Comando desconhecido - tenta executar diretamente no executor
                success = self._handle_unknown_command(command, parameter)
            
            # Atualiza estatísticas
            if success:
                self.stats["successful_actions"] += 1
            else:
                self.stats["failed_actions"] += 1
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao executar ação: {e}")
            self.stats["failed_actions"] += 1
            return False
    
    def _log_internal_monologue(self, monologue: str):
        """Log do monólogo interno do Kairo"""
        if monologue and isinstance(monologue, str):
            self.logger.info(f"INTERNAL_MONOLOGUE: {monologue}")
    
    def _handle_speak(self, parameter: Any) -> bool:
        """Executa comando de fala"""
        try:
            if isinstance(parameter, dict):
                text = parameter.get("text", str(parameter))
            else:
                text = str(parameter)
            
            if not text:
                return False
            
            # Registra na memória
            self.state_manager.add_interaction("kairo", text)
            
            # Executa no executor específico
            return self.executor.execute_action("speak", {"text": text})
            
        except Exception as e:
            self.logger.error(f"Erro em speak: {e}")
            return False
    
    def _handle_think(self, parameter: Any) -> bool:
        """Executa comando de pensamento"""
        try:
            thought = str(parameter) if parameter else ""
            
            if thought:
                self.logger.info(f"THOUGHT: {thought}")
                
                # Pode executar ação visual no executor se suportado
                return self.executor.execute_action("show_thought", {"text": thought})
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em think: {e}")
            return False
    
    def _handle_express_emotion(self, parameter: Any) -> bool:
        """Executa comando de expressão emocional"""
        try:
            if not isinstance(parameter, dict):
                return False
            
            emotion = parameter.get("emotion")
            intensity = parameter.get("intensity", 5.0)
            
            if not emotion:
                return False
            
            # Executa no executor específico (que decidirá como expressar)
            return self.executor.execute_action("express_emotion", {
                "emotion": emotion,
                "intensity": intensity
            })
            
        except Exception as e:
            self.logger.error(f"Erro em express_emotion: {e}")
            return False
    
    def _handle_adjust_emotion(self, parameter: Any) -> bool:
        """Executa comando de ajuste emocional"""
        try:
            if not isinstance(parameter, dict):
                return False
            
            for emotion, delta in parameter.items():
                if isinstance(delta, (int, float)):
                    self.state_manager.update_emotional_state(emotion, delta, "self_adjustment")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em adjust_emotion: {e}")
            return False
    
    def _handle_update_personality(self, parameter: Any) -> bool:
        """Executa comando de atualização de personalidade"""
        try:
            if not isinstance(parameter, dict):
                return False
            
            for trait, delta in parameter.items():
                if isinstance(delta, (int, float)):
                    self.state_manager.update_personality_trait(trait, delta, "self_adjustment")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em update_personality: {e}")
            return False
    
    def _handle_ask_question(self, parameter: Any) -> bool:
        """Executa comando de pergunta"""
        try:
            if isinstance(parameter, dict):
                question = parameter.get("question", str(parameter))
            else:
                question = str(parameter)
            
            if not question:
                return False
            
            # Registra na memória
            self.state_manager.add_interaction("kairo", question)
            
            # Executa no executor específico
            return self.executor.execute_action("ask_question", {"text": question})
            
        except Exception as e:
            self.logger.error(f"Erro em ask_question: {e}")
            return False
    
    def _handle_request_clarification(self, parameter: Any) -> bool:
        """Executa comando de pedido de esclarecimento"""
        try:
            if isinstance(parameter, dict):
                request = parameter.get("request", str(parameter))
            else:
                request = str(parameter)
            
            if not request:
                return False
            
            # Registra na memória
            self.state_manager.add_interaction("kairo", request)
            
            # Executa no executor específico
            return self.executor.execute_action("request_clarification", {"text": request})
            
        except Exception as e:
            self.logger.error(f"Erro em request_clarification: {e}")
            return False
    
    def _handle_add_user_fact(self, parameter: Any) -> bool:
        """Executa comando de adição de fato sobre usuário"""
        try:
            fact = str(parameter) if parameter else ""
            
            if fact:
                user_id = self.state_manager.get_current_user_id()
                self.state_manager.add_user_fact(user_id, fact)
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro em add_user_fact: {e}")
            return False
    
    def _handle_update_user_profile(self, parameter: Any) -> bool:
        """Executa comando de atualização de perfil do usuário"""
        try:
            if not isinstance(parameter, dict):
                return False
            
            user_id = self.state_manager.get_current_user_id()
            
            for field, value in parameter.items():
                self.state_manager.update_user_profile(user_id, field, value)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro em update_user_profile: {e}")
            return False
    
    def _handle_remember_important(self, parameter: Any) -> bool:
        """Executa comando de memorização de informação importante"""
        try:
            info = str(parameter) if parameter else ""
            
            if info:
                # Adiciona como interação com alta importância
                interaction = self.state_manager.add_interaction("kairo", f"[IMPORTANTE] {info}")
                # Força alta importância
                if interaction:
                    interaction["importance"] = 1.0
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Erro em remember_important: {e}")
            return False
    
    def _handle_executor_action(self, parameter: Any) -> bool:
        """Executa ação específica do executor"""
        try:
            if not isinstance(parameter, dict):
                return False
            
            action_name = parameter.get("action")
            action_params = parameter.get("params", {})
            
            if not action_name:
                return False
            
            # Executa diretamente no executor
            return self.executor.execute_action(action_name, action_params)
            
        except Exception as e:
            self.logger.error(f"Erro em executor_action: {e}")
            return False
    
    def _handle_unknown_command(self, command: str, parameter: Any) -> bool:
        """Tenta executar comando desconhecido diretamente no executor"""
        try:
            self.logger.warning(f"Comando desconhecido: {command}")
            
            # Verifica se o executor suporta este comando
            available_actions = self.get_available_actions()
            
            if command in available_actions:
                return self.executor.execute_action(command, parameter)
            else:
                self.logger.error(f"Comando {command} não suportado pelo executor")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao executar comando desconhecido {command}: {e}")
            return False
    
    def get_available_actions(self) -> List[str]:
        """
        Obtém lista de ações disponíveis
        
        Returns:
            Lista de comandos disponíveis
        """
        try:
            # Ações básicas do Maestro
            maestro_actions = list(self.command_handlers.keys())
            
            # Ações específicas do executor
            executor_actions = []
            if hasattr(self.executor, "get_available_actions"):
                executor_actions = self.executor.get_available_actions()
            
            # Combina ambas
            all_actions = maestro_actions + executor_actions
            
            return list(set(all_actions))  # Remove duplicatas
            
        except Exception as e:
            self.logger.error(f"Erro ao obter ações disponíveis: {e}")
            return list(self.command_handlers.keys())
    
    def get_action_description(self, action: str) -> str:
        """
        Obtém descrição de uma ação
        
        Args:
            action: Nome da ação
            
        Returns:
            Descrição da ação
        """
        descriptions = {
            "speak": "Falar com o usuário (parameter: texto ou {text: string})",
            "think": "Expressar pensamento interno (parameter: texto)",
            "express_emotion": "Expressar emoção (parameter: {emotion: string, intensity: float})",
            "adjust_emotion": "Ajustar estado emocional (parameter: {emotion: delta})",
            "update_personality": "Atualizar traço de personalidade (parameter: {trait: delta})",
            "ask_question": "Fazer pergunta ao usuário (parameter: texto ou {question: string})",
            "request_clarification": "Pedir esclarecimento (parameter: texto ou {request: string})",
            "add_user_fact": "Adicionar fato sobre usuário (parameter: texto)",
            "update_user_profile": "Atualizar perfil do usuário (parameter: {field: value})",
            "remember_important": "Memorizar informação importante (parameter: texto)",
            "executor_action": "Ação específica do executor (parameter: {action: string, params: dict})"
        }
        
        if action in descriptions:
            return descriptions[action]
        
        # Tenta obter descrição do executor
        if hasattr(self.executor, "get_action_description"):
            return self.executor.get_action_description(action)
        
        return f"Ação {action} (descrição não disponível)"
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do executor"""
        success_rate = 0.0
        if self.stats["total_actions"] > 0:
            success_rate = (self.stats["successful_actions"] / self.stats["total_actions"]) * 100
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "available_actions_count": len(self.get_available_actions())
        }
    
    def shutdown(self):
        """Encerra o executor de ações"""
        self.logger.info("ActionExecutor encerrado")

if __name__ == "__main__":
    # Teste básico do ActionExecutor
    from modules.state_manager import StateManager
    
    # Mock executor simples para teste
    class MockExecutor:
        def get_available_actions(self):
            return ["mock_action", "test_action"]
        
        def execute_action(self, action, params):
            print(f"MockExecutor: {action} com {params}")
            return True
        
        def get_action_description(self, action):
            return f"Mock action: {action}"
    
    sm = StateManager()
    sm.initialize()
    
    mock_executor = MockExecutor()
    ae = ActionExecutor(mock_executor, sm)
    ae.initialize()
    
    # Testa execução de plano
    test_plan = {
        "internal_monologue": "Vou cumprimentar o usuário",
        "actions": [
            {"command": "speak", "parameter": "Olá! Como você está?"},
            {"command": "adjust_emotion", "parameter": {"joy": 0.5}},
            {"command": "express_emotion", "parameter": {"emotion": "joy", "intensity": 6.0}}
        ]
    }
    
    print("Executando plano de teste...")
    success = ae.execute_plan(test_plan)
    print(f"Resultado: {success}")
    
    print("\nAções disponíveis:")
    for action in ae.get_available_actions():
        print(f"  {action}: {ae.get_action_description(action)}")
    
    print("\nEstatísticas:")
    stats = ae.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    ae.shutdown()
    sm.shutdown()

