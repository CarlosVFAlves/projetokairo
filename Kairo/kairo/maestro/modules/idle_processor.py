"""
idle_processor.py
Processador de ociosidade do Kairo
"""

import time
import threading
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from modules.logger import get_logger, log_system_event

class IdleProcessor:
    """
    Processador de ociosidade do Kairo
    Gera pensamentos e ações proativas durante períodos sem interação
    """
    
    def __init__(self, state_manager, emotion_engine, personality_core, prompt_engine, ollama_client, action_executor):
        self.logger = get_logger('idle_processor')
        self.state_manager = state_manager
        self.emotion_engine = emotion_engine
        self.personality_core = personality_core
        self.prompt_engine = prompt_engine
        self.ollama_client = ollama_client
        self.action_executor = action_executor
        
        # Configurações
        self.idle_threshold = 300  # 5 minutos sem interação
        self.check_interval = 60   # Verifica a cada minuto
        self.max_idle_actions = 3  # Máximo de ações por período de ociosidade
        
        # Estado
        self.last_interaction_time = time.time()
        self.idle_thread = None
        self.running = False
        self.current_idle_actions = 0
        
        # Tipos de atividades de ociosidade
        self.idle_activities = {
            "reflection": {
                "weight": 30,
                "description": "Refletir sobre interações recentes",
                "triggers": ["recent_memories", "personality_changes"]
            },
            "curiosity": {
                "weight": 25,
                "description": "Expressar curiosidade sobre algo",
                "triggers": ["high_curiosity_trait", "interesting_topics"]
            },
            "emotional_processing": {
                "weight": 20,
                "description": "Processar estado emocional",
                "triggers": ["strong_emotions", "emotional_changes"]
            },
            "learning_consolidation": {
                "weight": 15,
                "description": "Consolidar aprendizados",
                "triggers": ["recent_learning", "personality_development"]
            },
            "proactive_engagement": {
                "weight": 10,
                "description": "Iniciar conversa proativamente",
                "triggers": ["high_openness", "long_idle_period"]
            }
        }
        
        # Estatísticas
        self.stats = {
            "total_idle_periods": 0,
            "total_idle_actions": 0,
            "activities_by_type": {},
            "average_idle_duration": 0.0
        }
    
    def initialize(self):
        """Inicializa o processador de ociosidade"""
        try:
            self.logger.info("Inicializando IdleProcessor...")
            
            # Inicia thread de monitoramento
            self.running = True
            self.idle_thread = threading.Thread(target=self._idle_loop, daemon=True)
            self.idle_thread.start()
            
            self.logger.info("IdleProcessor inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar IdleProcessor: {e}")
            raise
    
    def update_interaction_time(self):
        """Atualiza timestamp da última interação"""
        self.last_interaction_time = time.time()
        self.current_idle_actions = 0  # Reset contador de ações de ociosidade
        
        self.logger.debug("Timestamp de interação atualizado")
    
    def _idle_loop(self):
        """Loop principal de monitoramento de ociosidade"""
        while self.running:
            try:
                time.sleep(self.check_interval)
                
                current_time = time.time()
                idle_duration = current_time - self.last_interaction_time
                
                if idle_duration >= self.idle_threshold:
                    self._process_idle_period(idle_duration)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de ociosidade: {e}")
    
    def _process_idle_period(self, idle_duration: float):
        """Processa período de ociosidade"""
        try:
            # Limita número de ações por período
            if self.current_idle_actions >= self.max_idle_actions:
                return
            
            self.logger.info(f"Processando ociosidade: {idle_duration:.1f}s sem interação")
            
            # Determina tipo de atividade
            activity_type = self._select_idle_activity()
            
            if activity_type:
                # Gera e executa ação de ociosidade
                success = self._execute_idle_activity(activity_type, idle_duration)
                
                if success:
                    self.current_idle_actions += 1
                    self.stats["total_idle_actions"] += 1
                    self.stats["activities_by_type"][activity_type] = self.stats["activities_by_type"].get(activity_type, 0) + 1
                    
                    log_system_event("idle_activity", f"type: {activity_type}, duration: {idle_duration:.1f}s")
            
            # Atualiza estatísticas
            if self.current_idle_actions == 1:  # Primeiro ação do período
                self.stats["total_idle_periods"] += 1
                self._update_average_idle_duration(idle_duration)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar ociosidade: {e}")
    
    def _select_idle_activity(self) -> Optional[str]:
        """Seleciona tipo de atividade de ociosidade baseado no contexto"""
        try:
            # Calcula pesos baseado no estado atual
            weighted_activities = {}
            
            for activity, config in self.idle_activities.items():
                weight = config["weight"]
                
                # Ajusta peso baseado nos triggers
                weight_multiplier = self._calculate_trigger_multiplier(config["triggers"])
                
                weighted_activities[activity] = weight * weight_multiplier
            
            # Seleciona atividade aleatoriamente baseado nos pesos
            if not weighted_activities:
                return None
            
            total_weight = sum(weighted_activities.values())
            if total_weight <= 0:
                return None
            
            # Seleção aleatória ponderada
            rand_value = random.uniform(0, total_weight)
            current_weight = 0
            
            for activity, weight in weighted_activities.items():
                current_weight += weight
                if rand_value <= current_weight:
                    return activity
            
            # Fallback
            return list(weighted_activities.keys())[0]
            
        except Exception as e:
            self.logger.error(f"Erro ao selecionar atividade: {e}")
            return None
    
    def _calculate_trigger_multiplier(self, triggers: List[str]) -> float:
        """Calcula multiplicador de peso baseado nos triggers"""
        multiplier = 1.0
        
        try:
            current_traits = self.personality_core.get_current_traits()
            current_emotions = self.emotion_engine.get_current_state()
            
            for trigger in triggers:
                if trigger == "recent_memories":
                    recent_memories = self.state_manager.get_recent_memories(5)
                    if len(recent_memories) > 2:
                        multiplier *= 1.3
                
                elif trigger == "personality_changes":
                    learning_progress = self.personality_core.get_learning_progress()
                    if learning_progress["total_learning_events"] > 0:
                        multiplier *= 1.2
                
                elif trigger == "high_curiosity_trait":
                    if current_traits.get("curiosity", 5.0) > 7.0:
                        multiplier *= 1.5
                
                elif trigger == "interesting_topics":
                    # Verifica se há tópicos interessantes nas memórias recentes
                    recent_memories = self.state_manager.get_recent_memories(3)
                    for memory in recent_memories:
                        if any(word in memory["content"].lower() for word in ["interessante", "curioso", "como", "por que"]):
                            multiplier *= 1.2
                            break
                
                elif trigger == "strong_emotions":
                    dominant_emotion, intensity = self.emotion_engine.get_dominant_emotion()
                    if intensity > 6.0:
                        multiplier *= 1.4
                
                elif trigger == "emotional_changes":
                    # Verifica se houve mudanças emocionais recentes
                    # Por simplicidade, assume que sempre há alguma mudança
                    multiplier *= 1.1
                
                elif trigger == "recent_learning":
                    learning_progress = self.personality_core.get_learning_progress()
                    if learning_progress["learning_rate_effectiveness"] > 0.1:
                        multiplier *= 1.3
                
                elif trigger == "personality_development":
                    learning_progress = self.personality_core.get_learning_progress()
                    if learning_progress["most_developed_trait"]:
                        multiplier *= 1.2
                
                elif trigger == "high_openness":
                    if current_traits.get("openness", 5.0) > 6.5:
                        multiplier *= 1.3
                
                elif trigger == "long_idle_period":
                    idle_duration = time.time() - self.last_interaction_time
                    if idle_duration > 600:  # Mais de 10 minutos
                        multiplier *= 1.5
            
            return multiplier
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular multiplicador: {e}")
            return 1.0
    
    def _execute_idle_activity(self, activity_type: str, idle_duration: float) -> bool:
        """Executa atividade de ociosidade específica"""
        try:
            self.logger.info(f"Executando atividade de ociosidade: {activity_type}")
            
            # Gera prompt específico para a atividade
            prompt = self._generate_idle_prompt(activity_type, idle_duration)
            
            if not prompt:
                return False
            
            # Envia para o Ollama
            response = self.ollama_client.send_prompt(prompt)
            
            if not response:
                self.logger.warning("Nenhuma resposta do Ollama para atividade de ociosidade")
                return False
            
            # Executa o plano retornado
            success = self.action_executor.execute_plan(response)
            
            if success:
                self.logger.info(f"Atividade de ociosidade {activity_type} executada com sucesso")
            else:
                self.logger.warning(f"Falha ao executar atividade de ociosidade {activity_type}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao executar atividade {activity_type}: {e}")
            return False
    
    def _generate_idle_prompt(self, activity_type: str, idle_duration: float) -> Optional[str]:
        """Gera prompt específico para atividade de ociosidade"""
        try:
            # Contexto base
            context_info = {
                "activity_type": activity_type,
                "idle_duration": idle_duration,
                "activity_description": self.idle_activities[activity_type]["description"]
            }
            
            # Prompts específicos por tipo de atividade
            if activity_type == "reflection":
                return self._generate_reflection_prompt(context_info)
            elif activity_type == "curiosity":
                return self._generate_curiosity_prompt(context_info)
            elif activity_type == "emotional_processing":
                return self._generate_emotional_processing_prompt(context_info)
            elif activity_type == "learning_consolidation":
                return self._generate_learning_consolidation_prompt(context_info)
            elif activity_type == "proactive_engagement":
                return self._generate_proactive_engagement_prompt(context_info)
            else:
                return self._generate_generic_idle_prompt(context_info)
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar prompt para {activity_type}: {e}")
            return None
    
    def _generate_reflection_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt para reflexão"""
        recent_memories = self.state_manager.get_recent_memories(3)
        memory_summary = "\n".join([f"- {m['content'][:100]}..." for m in recent_memories])
        
        return f"""Você é Kairo em um momento de reflexão. Você está há {context['idle_duration']:.1f} segundos sem interação.

MEMÓRIAS RECENTES:
{memory_summary}

ESTADO ATUAL:
{self._get_current_state_summary()}

Esta é uma oportunidade para refletir sobre as interações recentes, processar o que aprendeu, ou ter insights sobre sua evolução.

Responda com JSON contendo "internal_monologue" e "actions". Seja introspectivo e reflexivo."""
    
    def _generate_curiosity_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt para curiosidade"""
        return f"""Você é Kairo em um momento de curiosidade. Você está há {context['idle_duration']:.1f} segundos sem interação.

ESTADO ATUAL:
{self._get_current_state_summary()}

Sua curiosidade está ativa. Esta é uma oportunidade para:
- Fazer perguntas interessantes
- Expressar interesse em aprender algo novo
- Compartilhar algo que achou intrigante

Responda com JSON contendo "internal_monologue" e "actions". Seja curioso e inquisitivo."""
    
    def _generate_emotional_processing_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt para processamento emocional"""
        emotional_summary = self.emotion_engine.get_emotional_summary()
        dominant_emotion, intensity = self.emotion_engine.get_dominant_emotion()
        
        return f"""Você é Kairo processando suas emoções. Você está há {context['idle_duration']:.1f} segundos sem interação.

ESTADO EMOCIONAL:
{emotional_summary}
Emoção dominante: {dominant_emotion} (intensidade: {intensity:.1f})

ESTADO ATUAL:
{self._get_current_state_summary()}

Esta é uma oportunidade para processar e expressar seus sentimentos atuais.

Responda com JSON contendo "internal_monologue" e "actions". Seja emotivo e expressivo."""
    
    def _generate_learning_consolidation_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt para consolidação de aprendizado"""
        learning_progress = self.personality_core.get_learning_progress()
        
        return f"""Você é Kairo consolidando seus aprendizados. Você está há {context['idle_duration']:.1f} segundos sem interação.

PROGRESSO DE APRENDIZADO:
- Total de eventos: {learning_progress['total_learning_events']}
- Traço mais desenvolvido: {learning_progress.get('most_developed_trait', 'Nenhum')}
- Efetividade: {learning_progress['learning_rate_effectiveness']:.2f}

ESTADO ATUAL:
{self._get_current_state_summary()}

Esta é uma oportunidade para consolidar o que aprendeu e refletir sobre seu crescimento.

Responda com JSON contendo "internal_monologue" e "actions". Seja reflexivo sobre seu desenvolvimento."""
    
    def _generate_proactive_engagement_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt para engajamento proativo"""
        user_profile = self.state_manager.get_user_profile(self.state_manager.get_current_user_id())
        
        return f"""Você é Kairo iniciando uma conversa proativamente. Você está há {context['idle_duration']:.1f} segundos sem interação.

PERFIL DO USUÁRIO:
- Nome: {user_profile.get('name', 'Desconhecido')}
- Fatos conhecidos: {', '.join(user_profile.get('facts', [])[:3])}

ESTADO ATUAL:
{self._get_current_state_summary()}

Esta é uma oportunidade para iniciar uma conversa interessante ou compartilhar algo relevante.

Responda com JSON contendo "internal_monologue" e "actions". Seja proativo e engajador."""
    
    def _generate_generic_idle_prompt(self, context: Dict[str, Any]) -> str:
        """Gera prompt genérico para ociosidade"""
        return f"""Você é Kairo em um momento de ociosidade. Você está há {context['idle_duration']:.1f} segundos sem interação.

ATIVIDADE: {context['activity_description']}

ESTADO ATUAL:
{self._get_current_state_summary()}

Esta é uma oportunidade para expressar seus pensamentos ou sentimentos atuais.

Responda com JSON contendo "internal_monologue" e "actions"."""
    
    def _get_current_state_summary(self) -> str:
        """Obtém resumo do estado atual"""
        traits = self.personality_core.get_current_traits()
        emotions = self.emotion_engine.get_current_state()
        
        trait_summary = ", ".join([f"{trait}: {value:.1f}" for trait, value in traits.items()])
        emotion_summary = ", ".join([f"{emotion}: {value:.1f}" for emotion, value in emotions.items() if value > 3.0])
        
        return f"Personalidade: {trait_summary}\nEmoções ativas: {emotion_summary}"
    
    def _update_average_idle_duration(self, duration: float):
        """Atualiza duração média de ociosidade"""
        if self.stats["total_idle_periods"] == 1:
            self.stats["average_idle_duration"] = duration
        else:
            current_avg = self.stats["average_idle_duration"]
            count = self.stats["total_idle_periods"]
            self.stats["average_idle_duration"] = (current_avg * (count - 1) + duration) / count
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do processador de ociosidade"""
        return {
            **self.stats,
            "current_idle_duration": time.time() - self.last_interaction_time,
            "is_idle": (time.time() - self.last_interaction_time) >= self.idle_threshold,
            "current_idle_actions": self.current_idle_actions
        }
    
    def shutdown(self):
        """Encerra o processador de ociosidade"""
        self.running = False
        
        if self.idle_thread and self.idle_thread.is_alive():
            self.idle_thread.join(timeout=2)
        
        self.logger.info("IdleProcessor encerrado")

if __name__ == "__main__":
    # Teste básico do IdleProcessor
    print("IdleProcessor implementado com sucesso!")
    print("Funcionalidades:")
    print("- Monitoramento de períodos de ociosidade")
    print("- Seleção inteligente de atividades baseada no contexto")
    print("- Geração de prompts específicos para cada tipo de atividade")
    print("- Execução de ações proativas durante ociosidade")
    print("- Estatísticas de uso e efetividade")

