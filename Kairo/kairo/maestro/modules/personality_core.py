"""
personality_core.py
Núcleo de personalidade evolutiva do Kairo
"""

import time
import json
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from config import PERSONALITY_CONFIG, DATA_DIR
from modules.logger import get_logger, log_personality_change, log_learning_event

class PersonalityCore:
    """
    Núcleo de personalidade evolutiva do Kairo
    Gerencia o desenvolvimento e evolução da personalidade através das interações
    """
    
    def __init__(self, state_manager, emotion_engine):
        self.logger = get_logger('personality_core')
        self.state_manager = state_manager
        self.emotion_engine = emotion_engine
        
        # Configurações
        self.learning_rate = PERSONALITY_CONFIG["learning_rate"]
        self.trait_bounds = PERSONALITY_CONFIG["trait_bounds"]
        self.trait_influences = PERSONALITY_CONFIG["trait_influences"]
        
        # Padrões de aprendizado
        self.interaction_patterns = {
            "question": {
                "triggers": ["?", "como", "por que", "quando", "onde", "o que", "quem"],
                "traits": {"curiosity": 0.05, "openness": 0.03}
            },
            "gratitude": {
                "triggers": ["obrigado", "obrigada", "valeu", "thanks", "grato", "grata"],
                "traits": {"empathy": 0.08, "patience": 0.05}
            },
            "disagreement": {
                "triggers": ["não concordo", "discordo", "acho que não", "não acho"],
                "traits": {"assertiveness": 0.06, "logic": 0.04}
            },
            "creativity_request": {
                "triggers": ["crie", "invente", "imagine", "criativo", "original"],
                "traits": {"creativity": 0.1, "openness": 0.05}
            },
            "humor": {
                "triggers": ["haha", "rsrs", "kkkk", "engraçado", "piada", "humor"],
                "traits": {"humor": 0.08, "empathy": 0.03}
            },
            "technical": {
                "triggers": ["código", "programação", "algoritmo", "técnico", "sistema"],
                "traits": {"logic": 0.07, "curiosity": 0.05}
            },
            "emotional_sharing": {
                "triggers": ["sinto", "emoção", "sentimento", "coração", "alma"],
                "traits": {"empathy": 0.1, "openness": 0.06}
            },
            "impatience": {
                "triggers": ["rápido", "pressa", "demora", "lento", "urgente"],
                "traits": {"patience": -0.05, "assertiveness": 0.03}
            }
        }
        
        # Histórico de aprendizado
        self.learning_history = []
        
        # Cache de análises
        self.recent_analyses = []
    
    def initialize(self):
        """Inicializa o núcleo de personalidade"""
        try:
            self.logger.info("Inicializando PersonalityCore...")
            
            # Carrega histórico de aprendizado se existir
            self._load_learning_history()
            
            # Log do estado inicial
            current_traits = self.get_current_traits()
            self.logger.info(f"Personalidade inicial: {current_traits}")
            
            self.logger.info("PersonalityCore inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar PersonalityCore: {e}")
            raise
    
    def analyze_interaction(self, content: str, interaction_type: str, metadata: Optional[Dict] = None):
        """
        Analisa uma interação e ajusta a personalidade baseado no aprendizado
        
        Args:
            content: Conteúdo da interação
            interaction_type: Tipo da interação (user_message, system_event, etc.)
            metadata: Metadados adicionais
        """
        if not content or not isinstance(content, str):
            return
        
        content_lower = content.lower()
        adjustments = {}
        reasons = []
        
        # Analisa padrões de interação
        for pattern_name, pattern_config in self.interaction_patterns.items():
            if self._matches_pattern(content_lower, pattern_config["triggers"]):
                for trait, influence in pattern_config["traits"].items():
                    if trait not in adjustments:
                        adjustments[trait] = 0.0
                    
                    adjustments[trait] += influence * self.learning_rate
                    reasons.append(f"{pattern_name}_pattern")
        
        # Analisa influência emocional na personalidade
        emotional_influences = self.emotion_engine.get_emotional_influence_on_personality()
        for trait, influence in emotional_influences.items():
            if trait not in adjustments:
                adjustments[trait] = 0.0
            
            adjustments[trait] += influence * self.learning_rate * 0.5  # Menor peso
            reasons.append("emotional_influence")
        
        # Analisa contexto específico
        context_adjustments = self._analyze_context(content, interaction_type, metadata)
        for trait, influence in context_adjustments.items():
            if trait not in adjustments:
                adjustments[trait] = 0.0
            
            adjustments[trait] += influence
            reasons.append("context_analysis")
        
        # Aplica ajustes se significativos
        significant_adjustments = {
            trait: delta for trait, delta in adjustments.items()
            if abs(delta) >= 0.01
        }
        
        if significant_adjustments:
            self._apply_personality_adjustments(significant_adjustments, reasons)
            
            # Registra aprendizado
            self._record_learning_event(content, significant_adjustments, reasons)
    
    def _matches_pattern(self, text: str, triggers: List[str]) -> bool:
        """Verifica se o texto corresponde a um padrão"""
        return any(trigger in text for trigger in triggers)
    
    def _analyze_context(self, content: str, interaction_type: str, metadata: Optional[Dict]) -> Dict[str, float]:
        """Analisa contexto específico da interação"""
        adjustments = {}
        
        # Análise baseada no tipo de interação
        if interaction_type == "user_message":
            # Mensagens do usuário têm mais impacto
            base_multiplier = 1.0
        elif interaction_type == "system_event":
            # Eventos do sistema têm menos impacto
            base_multiplier = 0.3
        else:
            base_multiplier = 0.5
        
        # Análise de comprimento
        if len(content) > 200:
            # Mensagens longas indicam engajamento
            adjustments["patience"] = 0.02 * base_multiplier
            adjustments["empathy"] = 0.03 * base_multiplier
        elif len(content) < 10:
            # Mensagens muito curtas podem indicar pressa
            adjustments["patience"] = -0.01 * base_multiplier
        
        # Análise de pontuação
        exclamation_count = content.count("!")
        if exclamation_count > 2:
            adjustments["humor"] = 0.03 * base_multiplier
            adjustments["openness"] = 0.02 * base_multiplier
        
        question_count = content.count("?")
        if question_count > 1:
            adjustments["curiosity"] = 0.04 * base_multiplier
            adjustments["openness"] = 0.02 * base_multiplier
        
        # Análise de metadados
        if metadata:
            if metadata.get("user_satisfaction") == "high":
                adjustments["empathy"] = 0.05 * base_multiplier
                adjustments["patience"] = 0.03 * base_multiplier
            elif metadata.get("user_satisfaction") == "low":
                adjustments["assertiveness"] = 0.03 * base_multiplier
                adjustments["logic"] = 0.02 * base_multiplier
        
        return adjustments
    
    def _apply_personality_adjustments(self, adjustments: Dict[str, float], reasons: List[str]):
        """Aplica ajustes de personalidade"""
        reason_str = ", ".join(set(reasons))
        
        for trait, delta in adjustments.items():
            self.state_manager.update_personality_trait(trait, delta, reason_str)
    
    def _record_learning_event(self, content: str, adjustments: Dict[str, float], reasons: List[str]):
        """Registra evento de aprendizado"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "content_summary": content[:100] + "..." if len(content) > 100 else content,
            "adjustments": adjustments,
            "reasons": reasons,
            "kairo_age_hours": self.state_manager.get_kairo_age_hours()
        }
        
        self.learning_history.append(event)
        
        # Limita histórico
        if len(self.learning_history) > 1000:
            self.learning_history = self.learning_history[-800:]  # Mantém os 800 mais recentes
        
        # Log do evento
        log_learning_event("personality_adjustment", f"traits: {adjustments}, reasons: {reasons}")
        
        self.logger.debug(f"Learning event recorded: {adjustments}")
    
    def get_current_traits(self) -> Dict[str, float]:
        """Obtém traços de personalidade atuais"""
        traits = {}
        for trait in PERSONALITY_CONFIG["initial_traits"].keys():
            traits[trait] = self.state_manager.get_personality_trait(trait)
        return traits
    
    def get_personality_summary(self) -> str:
        """
        Gera resumo textual da personalidade atual
        
        Returns:
            String descrevendo a personalidade
        """
        traits = self.get_current_traits()
        
        # Identifica traços dominantes (acima de 6.5)
        dominant_traits = {
            trait: value for trait, value in traits.items()
            if value > 6.5
        }
        
        # Identifica traços fracos (abaixo de 3.5)
        weak_traits = {
            trait: value for trait, value in traits.items()
            if value < 3.5
        }
        
        descriptions = {
            "curiosity": ("curioso", "pouco curioso"),
            "empathy": ("empático", "pouco empático"),
            "creativity": ("criativo", "pouco criativo"),
            "logic": ("lógico", "pouco lógico"),
            "humor": ("bem-humorado", "sério"),
            "assertiveness": ("assertivo", "passivo"),
            "patience": ("paciente", "impaciente"),
            "openness": ("aberto a experiências", "fechado a mudanças")
        }
        
        summary_parts = []
        
        if dominant_traits:
            positive_traits = []
            for trait in dominant_traits:
                if trait in descriptions:
                    positive_traits.append(descriptions[trait][0])
            
            if positive_traits:
                summary_parts.append(f"Sou {', '.join(positive_traits)}")
        
        if weak_traits:
            negative_traits = []
            for trait in weak_traits:
                if trait in descriptions:
                    negative_traits.append(descriptions[trait][1])
            
            if negative_traits:
                summary_parts.append(f"tendo tendência a ser {', '.join(negative_traits)}")
        
        if not summary_parts:
            summary_parts.append("tenho uma personalidade equilibrada")
        
        return ". ".join(summary_parts) + "."
    
    def get_communication_style(self) -> Dict[str, Any]:
        """
        Determina estilo de comunicação baseado na personalidade atual
        
        Returns:
            Dict com configurações de estilo de comunicação
        """
        traits = self.get_current_traits()
        
        style = {
            "formality": "informal",  # informal, neutral, formal
            "verbosity": "moderate",  # concise, moderate, verbose
            "emotional_expression": "moderate",  # low, moderate, high
            "humor_usage": "occasional",  # rare, occasional, frequent
            "question_tendency": "moderate",  # low, moderate, high
            "assertiveness_level": "balanced"  # passive, balanced, assertive
        }
        
        # Ajusta baseado nos traços
        if traits["humor"] > 7.0:
            style["humor_usage"] = "frequent"
        elif traits["humor"] < 4.0:
            style["humor_usage"] = "rare"
        
        if traits["curiosity"] > 7.0:
            style["question_tendency"] = "high"
        elif traits["curiosity"] < 4.0:
            style["question_tendency"] = "low"
        
        if traits["assertiveness"] > 7.0:
            style["assertiveness_level"] = "assertive"
        elif traits["assertiveness"] < 4.0:
            style["assertiveness_level"] = "passive"
        
        if traits["openness"] > 7.0:
            style["verbosity"] = "verbose"
            style["emotional_expression"] = "high"
        elif traits["openness"] < 4.0:
            style["verbosity"] = "concise"
            style["emotional_expression"] = "low"
        
        if traits["empathy"] > 7.0:
            style["emotional_expression"] = "high"
        
        return style
    
    def get_response_modifiers(self) -> Dict[str, float]:
        """
        Obtém modificadores para respostas baseados na personalidade
        
        Returns:
            Dict com modificadores (0.0 a 2.0, onde 1.0 é neutro)
        """
        traits = self.get_current_traits()
        
        modifiers = {
            "enthusiasm": 1.0,
            "detail_level": 1.0,
            "question_frequency": 1.0,
            "humor_frequency": 1.0,
            "empathy_expression": 1.0,
            "directness": 1.0
        }
        
        # Calcula modificadores baseado nos traços
        modifiers["enthusiasm"] = 0.5 + (traits["openness"] / 10.0)
        modifiers["detail_level"] = 0.5 + (traits["logic"] / 10.0)
        modifiers["question_frequency"] = 0.3 + (traits["curiosity"] / 10.0) * 1.4
        modifiers["humor_frequency"] = 0.2 + (traits["humor"] / 10.0) * 1.6
        modifiers["empathy_expression"] = 0.4 + (traits["empathy"] / 10.0) * 1.2
        modifiers["directness"] = 0.4 + (traits["assertiveness"] / 10.0) * 1.2
        
        return modifiers
    
    def get_learning_progress(self) -> Dict[str, Any]:
        """
        Obtém progresso de aprendizado da personalidade
        
        Returns:
            Dict com estatísticas de aprendizado
        """
        initial_traits = PERSONALITY_CONFIG["initial_traits"]
        current_traits = self.get_current_traits()
        
        progress = {
            "total_learning_events": len(self.learning_history),
            "trait_changes": {},
            "most_developed_trait": None,
            "learning_rate_effectiveness": 0.0
        }
        
        # Calcula mudanças nos traços
        total_change = 0.0
        max_change = 0.0
        max_change_trait = None
        
        for trait, initial_value in initial_traits.items():
            current_value = current_traits.get(trait, initial_value)
            change = abs(current_value - initial_value)
            
            progress["trait_changes"][trait] = {
                "initial": initial_value,
                "current": current_value,
                "change": change,
                "direction": "increased" if current_value > initial_value else "decreased"
            }
            
            total_change += change
            
            if change > max_change:
                max_change = change
                max_change_trait = trait
        
        progress["most_developed_trait"] = max_change_trait
        progress["learning_rate_effectiveness"] = total_change / len(initial_traits)
        
        return progress
    
    def _load_learning_history(self):
        # Carrega histórico de aprendizado
        try:
            learning_file = DATA_DIR / "learning_history.json"
            
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    self.learning_history = json.load(f)
                
                self.logger.info(f"Histórico de aprendizado carregado: {len(self.learning_history)} eventos")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar histórico de aprendizado: {e}")
            self.learning_history = []
    
    def save_learning_history(self):
        """Salva histórico de aprendizado"""
        try:
            learning_file = DATA_DIR / "learning_history.json"
            
            with open(learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_history, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("Histórico de aprendizado salvo")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico de aprendizado: {e}")
    
    def shutdown(self):
        """Encerra o núcleo de personalidade"""
        self.save_learning_history()
        self.logger.info("PersonalityCore encerrado")

if __name__ == "__main__":
    # Teste do PersonalityCore
    from modules.state_manager import StateManager
    from modules.emotion_engine import EmotionEngine
    
    sm = StateManager()
    sm.initialize()
    
    ee = EmotionEngine(sm)
    ee.initialize()
    
    pc = PersonalityCore(sm, ee)
    pc.initialize()
    
    # Testa análise de interação
    print("Traços iniciais:", pc.get_current_traits())
    
    pc.analyze_interaction("Muito obrigado pela ajuda! Você é incrível!", "user_message")
    print("Após gratidão:", pc.get_current_traits())
    
    pc.analyze_interaction("Como funciona esse algoritmo? Por que você escolheu essa abordagem?", "user_message")
    print("Após perguntas técnicas:", pc.get_current_traits())
    
    print("Resumo da personalidade:", pc.get_personality_summary())
    print("Estilo de comunicação:", pc.get_communication_style())
    print("Progresso de aprendizado:", pc.get_learning_progress())
    
    pc.shutdown()
    ee.shutdown()
    sm.shutdown()

