"""
emotion_engine.py
Sistema emocional do Kairo
"""

import time
import threading
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

from config import EMOTION_CONFIG
from modules.logger import get_logger, log_emotion_change

class EmotionEngine:
    """
    Motor emocional do Kairo
    Gerencia o estado emocional e sua evolução ao longo do tempo
    """
    
    def __init__(self, state_manager):
        self.logger = get_logger('emotion_engine')
        self.state_manager = state_manager
        
        # Configurações
        self.emotions = EMOTION_CONFIG["emotions"]
        self.decay_rates = EMOTION_CONFIG["decay_rates"]
        self.bounds = EMOTION_CONFIG["bounds"]
        
        # Estado interno
        self.last_decay_time = time.time()
        self.decay_thread = None
        self.running = False
        
        # Fatores de análise de texto
        self.emotion_triggers = {
            "joy": {
                "words": ["feliz", "alegre", "contente", "satisfeito", "animado", "eufórico", 
                         "ótimo", "excelente", "maravilhoso", "fantástico", "genial", "incrível",
                         "haha", "rsrs", "kkkk", "legal", "bacana", "massa", "show"],
                "patterns": ["!", "😊", "😄", "😃", "🎉", "👏"],
                "multiplier": 1.0
            },
            "sadness": {
                "words": ["triste", "deprimido", "melancólico", "desanimado", "chateado",
                         "decepcionado", "frustrado", "péssimo", "horrível", "terrível",
                         "chorar", "lágrimas", "saudade", "solidão"],
                "patterns": ["😢", "😭", "😞", "☹️", "💔"],
                "multiplier": 0.8
            },
            "anger": {
                "words": ["raiva", "irritado", "furioso", "puto", "bravo", "nervoso",
                         "ódio", "detesto", "odeio", "inferno", "droga", "merda",
                         "idiota", "estúpido", "ridículo", "absurdo"],
                "patterns": ["😠", "😡", "🤬", "💢", "!!!"],
                "multiplier": 1.2
            },
            "fear": {
                "words": ["medo", "assustado", "aterrorizado", "ansioso", "preocupado",
                         "nervoso", "tenso", "inseguro", "receoso", "apreensivo"],
                "patterns": ["😨", "😰", "😱", "😟", "😧"],
                "multiplier": 0.9
            },
            "surprise": {
                "words": ["surpreso", "chocado", "impressionado", "espantado", "uau",
                         "nossa", "caramba", "inacreditável", "inesperado"],
                "patterns": ["😲", "😮", "😯", "🤯", "?!"],
                "multiplier": 1.5
            },
            "interest": {
                "words": ["interessante", "curioso", "fascinante", "intrigante", "legal",
                         "bacana", "conte mais", "explique", "como", "por que", "quando",
                         "onde", "quero saber", "me ensina"],
                "patterns": ["?", "🤔", "💭", "📚", "🔍"],
                "multiplier": 1.1
            }
        }
        
        # Restrições emocionais (emoções que se inibem mutuamente)
        self.emotional_constraints = [
            ("joy", "sadness", 0.7),      # Alegria reduz tristeza
            ("sadness", "joy", 0.5),      # Tristeza reduz alegria
            ("anger", "fear", 0.3),       # Raiva reduz medo
            ("fear", "anger", 0.3),       # Medo reduz raiva
            ("surprise", "sadness", 0.4), # Surpresa reduz tristeza
            ("interest", "anger", 0.2)    # Interesse reduz raiva
        ]
    
    def initialize(self):
        """Inicializa o motor emocional"""
        try:
            self.logger.info("Inicializando EmotionEngine...")
            
            # Inicia thread de decaimento emocional
            self.running = True
            self.decay_thread = threading.Thread(target=self._decay_loop, daemon=True)
            self.decay_thread.start()
            
            self.logger.info("EmotionEngine inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar EmotionEngine: {e}")
            raise
    
    def analyze_text(self, text: str, author: str = "user") -> Dict[str, float]:
        """
        Analisa um texto e ajusta as emoções baseado no conteúdo
        
        Args:
            text: Texto a ser analisado
            author: Autor do texto (user, kairo, etc.)
            
        Returns:
            Dict com os ajustes emocionais aplicados
        """
        if not text or not isinstance(text, str):
            return {}
        
        text_lower = text.lower()
        adjustments = {}
        
        # Analisa cada emoção
        for emotion, config in self.emotion_triggers.items():
            intensity = 0.0
            
            # Verifica palavras-chave
            for word in config["words"]:
                if word in text_lower:
                    intensity += 0.3
            
            # Verifica padrões
            for pattern in config["patterns"]:
                if pattern in text:
                    intensity += 0.2
            
            # Aplica multiplicador específico da emoção
            intensity *= config["multiplier"]
            
            # Ajusta baseado no autor
            if author == "user":
                intensity *= 1.2  # Input do usuário tem mais impacto
            elif author == "kairo":
                intensity *= 0.8  # Próprias palavras têm menos impacto
            
            # Ajusta baseado no comprimento do texto
            length_factor = min(1.5, len(text) / 100)
            intensity *= length_factor
            
            if intensity > 0.1:  # Apenas ajustes significativos
                adjustments[emotion] = intensity
        
        # Aplica os ajustes
        if adjustments:
            self._apply_emotion_adjustments(adjustments, f"text_analysis: {text[:30]}...")
        
        return adjustments
    
    def trigger_emotion(self, emotion: str, intensity: float, reason: str = ""):
        """
        Dispara uma emoção específica
        
        Args:
            emotion: Nome da emoção
            intensity: Intensidade (0.0 a 10.0)
            reason: Razão do disparo
        """
        if emotion not in self.emotions:
            self.logger.warning(f"Emoção desconhecida: {emotion}")
            return
        
        adjustments = {emotion: intensity}
        self._apply_emotion_adjustments(adjustments, reason)
    
    def _apply_emotion_adjustments(self, adjustments: Dict[str, float], reason: str):
        """Aplica ajustes emocionais com restrições"""
        current_state = self.state_manager.get_emotional_state()
        
        # Aplica ajustes diretos
        for emotion, delta in adjustments.items():
            if emotion in self.emotions:
                self.state_manager.update_emotional_state(emotion, delta, reason)
        
        # Aplica restrições emocionais
        self._apply_emotional_constraints(adjustments)
        
        # Log do estado resultante
        new_state = self.state_manager.get_emotional_state()
        self.logger.debug(f"Emotion adjustments applied: {adjustments} -> {new_state}")
    
    def _apply_emotional_constraints(self, triggered_emotions: Dict[str, float]):
        """Aplica restrições entre emoções opostas"""
        current_state = self.state_manager.get_emotional_state()
        
        for emotion1, emotion2, inhibition_factor in self.emotional_constraints:
            if emotion1 in triggered_emotions and triggered_emotions[emotion1] > 0:
                # Emoção 1 foi ativada, reduz emoção 2
                current_value = current_state.get(emotion2, 0.0)
                if current_value > 0:
                    reduction = triggered_emotions[emotion1] * inhibition_factor
                    self.state_manager.update_emotional_state(
                        emotion2, -reduction, f"inhibited_by_{emotion1}"
                    )
    
    def get_current_state(self) -> Dict[str, float]:
        """Obtém estado emocional atual"""
        return self.state_manager.get_emotional_state()
    
    def get_dominant_emotion(self) -> Tuple[str, float]:
        """
        Obtém a emoção dominante atual
        
        Returns:
            Tupla (nome_da_emoção, intensidade)
        """
        current_state = self.get_current_state()
        
        # Filtra emoções neutras
        significant_emotions = {
            emotion: value for emotion, value in current_state.items()
            if value > 3.0  # Acima do neutro
        }
        
        if not significant_emotions:
            return ("neutral", 0.0)
        
        dominant_emotion = max(significant_emotions.items(), key=lambda x: x[1])
        return dominant_emotion
    
    def get_emotional_color(self) -> str:
        """
        Obtém cor representativa do estado emocional atual
        
        Returns:
            Código hexadecimal da cor
        """
        dominant_emotion, intensity = self.get_dominant_emotion()
        
        color_map = {
            "joy": "#FFD700",      # Dourado
            "sadness": "#4682B4",  # Azul aço
            "anger": "#DC143C",    # Vermelho carmesim
            "fear": "#9370DB",     # Violeta médio
            "surprise": "#FF69B4", # Rosa choque
            "interest": "#32CD32", # Verde lima
            "neutral": "#E8F5FF"   # Azul claro neutro
        }
        
        base_color = color_map.get(dominant_emotion, color_map["neutral"])
        
        # Ajusta intensidade da cor baseado na intensidade da emoção
        if intensity > 7.0:
            # Emoção muito intensa - cor mais saturada
            return base_color
        elif intensity > 5.0:
            # Emoção moderada - cor um pouco mais clara
            return self._lighten_color(base_color, 0.2)
        else:
            # Emoção fraca - cor bem mais clara
            return self._lighten_color(base_color, 0.5)
    
    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Clareia uma cor hexadecimal"""
        try:
            # Remove o #
            hex_color = hex_color.lstrip('#')
            
            # Converte para RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Clareia
            r = int(r + (255 - r) * factor)
            g = int(g + (255 - g) * factor)
            b = int(b + (255 - b) * factor)
            
            # Converte de volta para hex
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except:
            return "#E8F5FF"  # Fallback
    
    def get_emotional_influence_on_personality(self) -> Dict[str, float]:
        """
        Calcula como o estado emocional atual deve influenciar a personalidade
        
        Returns:
            Dict com ajustes sugeridos para traços de personalidade
        """
        current_state = self.get_current_state()
        influences = {}
        
        # Mapeamento de emoções para traços de personalidade
        emotion_to_trait_map = {
            "joy": {"empathy": 0.1, "openness": 0.1, "patience": 0.05},
            "sadness": {"empathy": 0.05, "patience": -0.05, "assertiveness": -0.1},
            "anger": {"assertiveness": 0.1, "patience": -0.15, "empathy": -0.05},
            "fear": {"openness": -0.1, "assertiveness": -0.1, "patience": 0.05},
            "surprise": {"curiosity": 0.1, "openness": 0.05},
            "interest": {"curiosity": 0.15, "openness": 0.1, "creativity": 0.05}
        }
        
        for emotion, value in current_state.items():
            if emotion in emotion_to_trait_map and value > 5.0:
                # Emoção acima do neutro
                intensity_factor = (value - 5.0) / 5.0  # 0.0 a 1.0
                
                for trait, base_influence in emotion_to_trait_map[emotion].items():
                    if trait not in influences:
                        influences[trait] = 0.0
                    
                    influences[trait] += base_influence * intensity_factor
        
        return influences
    
    def _decay_loop(self):
        """Loop de decaimento emocional em thread separada"""
        while self.running:
            try:
                time.sleep(60)  # Verifica a cada minuto
                
                current_time = time.time()
                time_delta = (current_time - self.last_decay_time) / 60  # Em minutos
                
                if time_delta >= 1.0:  # Aplica decaimento a cada minuto
                    self._apply_emotional_decay(time_delta)
                    self.last_decay_time = current_time
                
            except Exception as e:
                self.logger.error(f"Erro no loop de decaimento emocional: {e}")
    
    def _apply_emotional_decay(self, time_delta_minutes: float):
        """Aplica decaimento natural das emoções"""
        current_state = self.get_current_state()
        
        for emotion in self.emotions:
            current_value = current_state.get(emotion, 0.0)
            decay_rate = self.decay_rates.get(emotion, 0.1)
            
            # Calcula decaimento
            if emotion in ["joy", "interest"]:
                # Emoções positivas decaem em direção ao neutro (5.0)
                if current_value > 5.0:
                    decay = decay_rate * time_delta_minutes
                    new_value = max(5.0, current_value - decay)
                elif current_value < 5.0:
                    decay = decay_rate * time_delta_minutes
                    new_value = min(5.0, current_value + decay)
                else:
                    continue  # Já está neutro
            else:
                # Emoções negativas decaem em direção a 0
                if current_value > 0:
                    decay = decay_rate * time_delta_minutes
                    new_value = max(0.0, current_value - decay)
                else:
                    continue  # Já está em 0
            
            # Aplica o decaimento se for significativo
            if abs(new_value - current_value) > 0.01:
                delta = new_value - current_value
                self.state_manager.update_emotional_state(
                    emotion, delta, "natural_decay"
                )
    
    def get_emotional_summary(self) -> str:
        """
        Gera um resumo textual do estado emocional atual
        
        Returns:
            String descrevendo o estado emocional
        """
        current_state = self.get_current_state()
        dominant_emotion, intensity = self.get_dominant_emotion()
        
        if dominant_emotion == "neutral":
            return "Estou me sentindo neutro e equilibrado."
        
        intensity_descriptions = {
            (0, 3): "levemente",
            (3, 5): "moderadamente",
            (5, 7): "bastante",
            (7, 9): "muito",
            (9, 10): "extremamente"
        }
        
        intensity_desc = "moderadamente"
        for (min_val, max_val), desc in intensity_descriptions.items():
            if min_val <= intensity < max_val:
                intensity_desc = desc
                break
        
        emotion_descriptions = {
            "joy": "feliz e animado",
            "sadness": "triste e melancólico",
            "anger": "irritado e frustrado",
            "fear": "ansioso e preocupado",
            "surprise": "surpreso e impressionado",
            "interest": "curioso e interessado"
        }
        
        emotion_desc = emotion_descriptions.get(dominant_emotion, dominant_emotion)
        
        return f"Estou me sentindo {intensity_desc} {emotion_desc}."
    
    def shutdown(self):
        """Encerra o motor emocional"""
        self.running = False
        
        if self.decay_thread and self.decay_thread.is_alive():
            self.decay_thread.join(timeout=2)
        
        self.logger.info("EmotionEngine encerrado")

if __name__ == "__main__":
    # Teste do EmotionEngine
    from modules.state_manager import StateManager
    
    sm = StateManager()
    sm.initialize()
    
    ee = EmotionEngine(sm)
    ee.initialize()
    
    # Testa análise de texto
    print("Estado inicial:", ee.get_current_state())
    
    ee.analyze_text("Estou muito feliz hoje! Que dia incrível!")
    print("Após texto positivo:", ee.get_current_state())
    print("Emoção dominante:", ee.get_dominant_emotion())
    print("Resumo:", ee.get_emotional_summary())
    
    ee.analyze_text("Estou triste e preocupado com isso...")
    print("Após texto negativo:", ee.get_current_state())
    print("Emoção dominante:", ee.get_dominant_emotion())
    print("Resumo:", ee.get_emotional_summary())
    
    ee.shutdown()
    sm.shutdown()

