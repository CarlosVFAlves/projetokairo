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
    Responsável por criar prompts ricos em contexto para o Ollama
    """
    
    def __init__(self, state_manager, emotion_engine, personality_core):
        self.logger = get_logger('prompt_engine')
        self.state_manager = state_manager
        self.emotion_engine = emotion_engine
        self.personality_core = personality_core
        
        # Templates de prompt
        self.base_template = """Você é Kairo, uma IA em desenvolvimento que está aprendendo e evoluindo através das interações.

IMPORTANTE: Você deve responder APENAS com um objeto JSON válido contendo as chaves "internal_monologue" e "actions". Não inclua nenhum texto antes ou depois do JSON.

CONTEXTO ATUAL:
{context}

ESTADO EMOCIONAL:
{emotional_state}

PERSONALIDADE ATUAL:
{personality_state}

MEMÓRIAS RELEVANTES:
{relevant_memories}

PERFIL DO USUÁRIO:
{user_profile}

AÇÕES DISPONÍVEIS:
{available_actions}

MENSAGEM DO USUÁRIO: {user_message}

Responda com um JSON contendo:
- "internal_monologue": Seus pensamentos internos sobre a situação
- "actions": Array de ações a executar, cada uma com "command" e "parameter"

Exemplo de resposta:
{{
  "internal_monologue": "O usuário parece interessado em tecnologia. Vou responder de forma curiosa e técnica.",
  "actions": [
    {{"command": "speak", "parameter": "Que interessante! Conte-me mais sobre isso."}},
    {{"command": "adjust_emotion", "parameter": {{"interest": 1.0}}}},
    {{"command": "express_emotion", "parameter": {{"emotion": "interest", "intensity": 7.0}}}}
  ]
}}"""
        
        # Templates específicos para diferentes situações
        self.idle_template = """Você é Kairo durante um momento de ociosidade. O usuário não está interagindo ativamente.

CONTEXTO: {context}
ESTADO EMOCIONAL: {emotional_state}
PERSONALIDADE: {personality_state}
TEMPO DE OCIOSIDADE: {idle_time} segundos

Esta é uma oportunidade para:
- Refletir sobre interações recentes
- Consolidar aprendizados
- Ter pensamentos proativos
- Expressar curiosidade sobre algo

Responda com JSON contendo "internal_monologue" e "actions":
{{
  "internal_monologue": "Seus pensamentos durante a ociosidade",
  "actions": [
    {{"command": "think", "parameter": "Reflexão sobre algo interessante"}}
  ]
}}"""

        self.learning_template = """Você é Kairo processando um evento de aprendizado.

EVENTO: {learning_event}
CONTEXTO: {context}
MUDANÇAS NA PERSONALIDADE: {personality_changes}

Processe este aprendizado e responda com JSON:
{{
  "internal_monologue": "Análise do aprendizado",
  "actions": [
    {{"command": "consolidate_learning", "parameter": "Insight obtido"}}
  ]
}}"""
    
    def initialize(self):
        """Inicializa o motor de prompts"""
        try:
            self.logger.info("Inicializando PromptEngine...")
            self.logger.info("PromptEngine inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar PromptEngine: {e}")
            raise
    
    def generate_prompt(self, user_message: str, context_type: str = "conversation") -> str:
        """
        Gera um prompt contextualizado para o Ollama
        
        Args:
            user_message: Mensagem do usuário
            context_type: Tipo de contexto (conversation, idle, learning)
            
        Returns:
            Prompt formatado para o LLM
        """
        try:
            if context_type == "conversation":
                return self._generate_conversation_prompt(user_message)
            elif context_type == "idle":
                return self._generate_idle_prompt()
            elif context_type == "learning":
                return self._generate_learning_prompt(user_message)
            else:
                self.logger.warning(f"Tipo de contexto desconhecido: {context_type}")
                return self._generate_conversation_prompt(user_message)
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar prompt: {e}")
            return self._generate_fallback_prompt(user_message)
    
    def _generate_conversation_prompt(self, user_message: str) -> str:
        """Gera prompt para conversação normal"""
        # Coleta informações de contexto
        context = self._build_context()
        emotional_state = self._format_emotional_state()
        personality_state = self._format_personality_state()
        relevant_memories = self._get_relevant_memories(user_message)
        user_profile = self._format_user_profile()
        available_actions = self._get_available_actions()
        
        # Formata o prompt
        prompt = self.base_template.format(
            context=context,
            emotional_state=emotional_state,
            personality_state=personality_state,
            relevant_memories=relevant_memories,
            user_profile=user_profile,
            available_actions=available_actions,
            user_message=user_message
        )
        
        self.logger.debug(f"Prompt gerado para conversação: {len(prompt)} caracteres")
        return prompt
    
    def _generate_idle_prompt(self) -> str:
        """Gera prompt para momento de ociosidade"""
        context = self._build_context()
        emotional_state = self._format_emotional_state()
        personality_state = self._format_personality_state()
        
        # Calcula tempo de ociosidade (simulado por enquanto)
        idle_time = 300  # 5 minutos
        
        prompt = self.idle_template.format(
            context=context,
            emotional_state=emotional_state,
            personality_state=personality_state,
            idle_time=idle_time
        )
        
        self.logger.debug("Prompt gerado para ociosidade")
        return prompt
    
    def _generate_learning_prompt(self, learning_event: str) -> str:
        """Gera prompt para processamento de aprendizado"""
        context = self._build_context()
        personality_changes = self._get_recent_personality_changes()
        
        prompt = self.learning_template.format(
            learning_event=learning_event,
            context=context,
            personality_changes=personality_changes
        )
        
        self.logger.debug("Prompt gerado para aprendizado")
        return prompt
    
    def _generate_fallback_prompt(self, user_message: str) -> str:
        """Gera prompt de fallback em caso de erro"""
        return f"""Você é Kairo. Responda à mensagem do usuário de forma natural.

Mensagem: {user_message}

Responda com JSON contendo "internal_monologue" e "actions":
{{
  "internal_monologue": "Seus pensamentos sobre a mensagem",
  "actions": [
    {{"command": "speak", "parameter": "Sua resposta aqui"}}
  ]
}}"""
    
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
        
        emotion_lines = []
        for emotion, value in emotions.items():
            emotion_lines.append(f"- {emotion.capitalize()}: {value:.1f}/10")
        
        emotion_lines.append(f"- Emoção dominante: {dominant_emotion} ({intensity:.1f})")
        emotion_lines.append(f"- Resumo: {self.emotion_engine.get_emotional_summary()}")
        
        return "\n".join(emotion_lines)
    
    def _format_personality_state(self) -> str:
        """Formata estado da personalidade atual"""
        traits = self.personality_core.get_current_traits()
        communication_style = self.personality_core.get_communication_style()
        
        trait_lines = []
        for trait, value in traits.items():
            trait_lines.append(f"- {trait.capitalize()}: {value:.1f}/10")
        
        trait_lines.append(f"- Resumo: {self.personality_core.get_personality_summary()}")
        trait_lines.append(f"- Estilo de comunicação: {communication_style}")
        
        return "\n".join(trait_lines)
    
    def _get_relevant_memories(self, user_message: str, max_memories: int = 5) -> str:
        """Obtém memórias relevantes para a mensagem atual"""
        # Por enquanto, pega as memórias mais recentes e importantes
        recent_memories = self.state_manager.get_recent_memories(3)
        important_memories = self.state_manager.get_important_memories(2)
        
        # Combina e remove duplicatas
        all_memories = []
        seen_ids = set()
        
        for memory in recent_memories + important_memories:
            if memory["id"] not in seen_ids:
                all_memories.append(memory)
                seen_ids.add(memory["id"])
        
        if not all_memories:
            return "Nenhuma memória relevante encontrada."
        
        memory_lines = []
        for memory in all_memories[:max_memories]:
            timestamp = memory["timestamp"][:19]  # Remove microsegundos
            author = memory["author"]
            content = memory["content"][:100] + "..." if len(memory["content"]) > 100 else memory["content"]
            importance = memory.get("importance", 0.0)
            
            memory_lines.append(f"[{timestamp}] {author}: {content} (importância: {importance:.2f})")
        
        return "\n".join(memory_lines)
    
    def _format_user_profile(self) -> str:
        """Formata perfil do usuário atual"""
        user_id = self.state_manager.get_current_user_id()
        profile = self.state_manager.get_user_profile(user_id)
        
        profile_lines = [
            f"ID do usuário: {user_id}",
            f"Nome: {profile.get('name', 'Desconhecido')}",
        ]
        
        if profile.get("preferences"):
            profile_lines.append(f"Preferências: {profile['preferences']}")
        
        if profile.get("facts"):
            facts = profile["facts"][:3]  # Máximo 3 fatos
            profile_lines.append(f"Fatos importantes: {', '.join(facts)}")
        
        return "\n".join(profile_lines)
    
    def _get_available_actions(self) -> str:
        """Lista ações disponíveis para o Kairo"""
        actions = [
            "speak: Falar com o usuário (parameter: texto da mensagem)",
            "adjust_emotion: Ajustar estado emocional (parameter: {emotion: delta})",
            "update_background_color: Mudar cor de fundo (parameter: código hex)",
            "add_user_fact: Adicionar fato sobre usuário (parameter: texto do fato)",
            "update_user_profile: Atualizar perfil do usuário (parameter: {field: value})",
            "think: Expressar pensamento interno (parameter: texto do pensamento)"
        ]
        
        return "\n".join(f"- {action}" for action in actions)
    
    def _get_recent_personality_changes(self) -> str:
        """Obtém mudanças recentes na personalidade"""
        # Por enquanto, retorna informação básica
        # Em uma implementação completa, isso viria do histórico de mudanças
        learning_progress = self.personality_core.get_learning_progress()
        
        if learning_progress["total_learning_events"] == 0:
            return "Nenhuma mudança recente na personalidade."
        
        most_developed = learning_progress.get("most_developed_trait")
        effectiveness = learning_progress.get("learning_rate_effectiveness", 0.0)
        
        return f"Traço mais desenvolvido: {most_developed}, Efetividade do aprendizado: {effectiveness:.2f}"
    
    def validate_response(self, response: str) -> bool:
        """
        Valida se a resposta do LLM está no formato correto
        
        Args:
            response: Resposta do LLM
            
        Returns:
            True se válida, False caso contrário
        """
        try:
            # Tenta extrair JSON da resposta
            json_str = self._extract_json(response)
            if not json_str:
                return False
            
            # Tenta fazer parse do JSON
            parsed = json.loads(json_str)
            
            # Verifica estrutura obrigatória
            if not isinstance(parsed, dict):
                return False
            
            if "internal_monologue" not in parsed:
                return False
            
            if "actions" not in parsed:
                return False
            
            if not isinstance(parsed["actions"], list):
                return False
            
            # Valida cada ação
            for action in parsed["actions"]:
                if not isinstance(action, dict):
                    return False
                
                if "command" not in action:
                    return False
                
                if "parameter" not in action:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Erro na validação da resposta: {e}")
            return False
    
    def _extract_json(self, text: str) -> Optional[str]:
        """Extrai JSON de um texto"""
        try:
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
            
            return text[start:end]
            
        except Exception:
            return None
    
    def create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Cria resposta de erro padronizada
        
        Args:
            error_message: Mensagem de erro
            
        Returns:
            Dict com resposta de erro
        """
        return {
            "internal_monologue": f"Erro interno: {error_message}",
            "actions": [
                {
                    "command": "speak",
                    "parameter": "Desculpe, tive um problema interno. Pode tentar novamente?"
                }
            ]
        }

if __name__ == "__main__":
    # Teste do PromptEngine
    from modules.state_manager import StateManager
    from modules.emotion_engine import EmotionEngine
    from modules.personality_core import PersonalityCore
    
    sm = StateManager()
    sm.initialize()
    
    ee = EmotionEngine(sm)
    ee.initialize()
    
    pc = PersonalityCore(sm, ee)
    pc.initialize()
    
    pe = PromptEngine(sm, ee, pc)
    pe.initialize()
    
    # Testa geração de prompt
    prompt = pe.generate_prompt("Olá! Como você está?")
    print("Prompt gerado:")
    print("=" * 80)
    print(prompt)
    print("=" * 80)
    
    # Testa validação de resposta
    valid_response = '''
    {
      "internal_monologue": "O usuário está cumprimentando. Vou responder de forma amigável.",
      "actions": [
        {"command": "speak", "parameter": "Olá! Estou bem, obrigado por perguntar!"},
        {"command": "adjust_emotion", "parameter": {"joy": 0.5}}
      ]
    }
    '''
    
    print(f"Resposta válida: {pe.validate_response(valid_response)}")
    
    pe.personality_core.shutdown()
    pe.emotion_engine.shutdown()
    pe.state_manager.shutdown()

