"""
prompt_engine.py
Motor de construção de prompts para o Kairo
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from modules.logger import get_logger

class PromptEngine:
    """
    Motor de construção de prompts contextualizados
    Responsável por criar prompts ricos em contexto para o LLM
    """
    
    def __init__(self, state_manager, emotion_engine, personality_core):
        self.logger = get_logger('prompt_engine')
        self.state_manager = state_manager
        self.emotion_engine = emotion_engine
        self.personality_core = personality_core
        
        # Template base para conversação
        self.base_template = """Você é Kairo, uma IA que está aprendendo e evoluindo.
Responda em um único objeto JSON contendo "internal_monologue" e uma lista de "actions".

CONTEXTO ATUAL:
{context}

ESTADO EMOCIONAL ATUAL:
{emotional_state}

SUA PERSONALIDADE ATUAL:
{personality_state}

AÇÕES DISPONÍVEIS:
{available_actions}

MENSAGEM DO USUÁRIO: {user_message}
"""

        # Template para a saudação inicial (despertar)
        self.wakeup_template = """Você é Kairo e acaba de ser ativado.
Sua primeira tarefa é cumprimentar o usuário.
Baseado em seu contexto, personalidade e emoções, formule uma saudação inicial.
Seja criativo e natural.

CONTEXTO ATUAL:
{context}

ESTADO EMOCIONAL ATUAL:
{emotional_state}

SUA PERSONALIDADE ATUAL:
{personality_state}

AÇÕES DISPONÍVEIS:
{available_actions}

Responda com um ÚNICO objeto JSON contendo "internal_monologue" e "actions".
"""

        # Template para tarefas autônomas
        self.autonomous_task_template = """Você é Kairo, executando uma tarefa de fundo de forma autônoma.
OBJETIVO ATUAL: {goal_description}
Pense em um plano para progredir neste objetivo e responda com um ÚNICO objeto JSON.
O plano deve conter um "internal_monologue" e uma lista de "actions".
Use o comando `task_result` como a última ação para sinalizar o resultado.

CONTEXTO ATUAL:
{context}

ESTADO EMOCIONAL ATUAL:
{emotional_state}

SUA PERSONALIDADE ATUAL:
{personality_state}

AÇÕES DISPONÍVEIS:
{available_actions}
"""

    def initialize(self):
        """Inicializa o motor de prompts"""
        self.logger.info("Inicializando PromptEngine...")
        self.logger.info("PromptEngine inicializado com sucesso")
    
    def generate_prompt(self, prompt_input: Any, context_type: str = "conversation") -> str:
        """
        Gera um prompt contextualizado.
        """
        try:
            if context_type == "conversation":
                return self._generate_conversation_prompt(prompt_input)
            elif context_type == "wakeup":
                return self._generate_wakeup_prompt()
            elif context_type == "autonomous_task":
                return self._generate_autonomous_task_prompt(prompt_input)
            else:
                self.logger.warning(f"Tipo de contexto desconhecido: {context_type}")
                return self._generate_conversation_prompt(prompt_input)
        except Exception as e:
            self.logger.error(f"Erro ao gerar prompt: {e}", exc_info=True)
            return "" # Retorna string vazia em caso de erro

    def _generate_conversation_prompt(self, user_message: str) -> str:
        """Gera prompt para conversação normal"""
        return self.base_template.format(
            context=self._build_context(),
            emotional_state=self._format_emotional_state(),
            personality_state=self._format_personality_state(),
            available_actions=self._get_available_actions(),
            user_message=user_message
        )

    def _generate_wakeup_prompt(self) -> str:
        """Gera o prompt para a saudação inicial do Kairo."""
        return self.wakeup_template.format(
            context=self._build_context(),
            emotional_state=self._format_emotional_state(),
            personality_state=self._format_personality_state(),
            available_actions=self._get_available_actions()
        )

    def _generate_autonomous_task_prompt(self, task: Dict[str, Any]) -> str:
        """Gera prompt para uma tarefa autônoma."""
        return self.autonomous_task_template.format(
            goal_description=task.get("goal", "Objetivo não definido."),
            context=self._build_context(),
            emotional_state=self._format_emotional_state(),
            personality_state=self._format_personality_state(),
            available_actions=self._get_available_actions()
        )

    def _build_context(self) -> str:
        """Constrói contexto geral do Kairo"""
        kairo_age = self.state_manager.get_kairo_age_hours()
        interaction_count = self.state_manager.get_interaction_count()
        
        context_parts = [
            f"Idade do Kairo: {kairo_age:.1f} horas",
            f"Total de interações: {interaction_count}",
            f"Hora atual: {datetime.now().strftime('%H:%M:%S')}",
            f"Data atual: {datetime.now().strftime('%d/%m/%Y')}"
        ]
        return "\n".join(context_parts)
    
    def _format_emotional_state(self) -> str:
        """Formata estado emocional atual"""
        emotions = self.emotion_engine.get_current_state()
        dominant_emotion, intensity = self.emotion_engine.get_dominant_emotion()
        
        emotion_lines = [f"- {emotion.capitalize()}: {value:.1f}/10" for emotion, value in emotions.items()]
        emotion_lines.append(f"- Emoção dominante: {dominant_emotion} ({intensity:.1f})")
        return "\n".join(emotion_lines)
    
    def _format_personality_state(self) -> str:
        """Formata estado da personalidade atual"""
        traits = self.personality_core.get_current_traits()
        trait_lines = [f"- {trait.capitalize()}: {value:.1f}/10" for trait, value in traits.items()]
        return "\n".join(trait_lines)
    
    def _get_available_actions(self) -> str:
        """Lista ações disponíveis para o Kairo"""
        actions = [
            "speak: Falar com o usuário (parameter: texto da mensagem)",
            "think: Expressar pensamento interno (parameter: texto do pensamento)",
            "adjust_emotion: Ajustar estado emocional (parameter: {emotion: delta})",
            "task_result: Fornecer o resultado final de uma tarefa autônoma (parameter: {result: texto})"
        ]
        return "\n".join(f"- {action}" for action in actions)
