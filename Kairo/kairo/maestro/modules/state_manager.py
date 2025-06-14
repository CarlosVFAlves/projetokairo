"""
state_manager.py
Módulo responsável pelo gerenciamento de estado e memória do Kairo
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import DATA_DIR, PROFILES_DIR, MEMORY_CONFIG, PERSONALITY_CONFIG, EMOTION_CONFIG
from modules.logger import get_logger, log_system_event, log_memory_consolidation

class StateManager:
    """
    Gerenciador de estado e memória do Kairo
    Responsável pela persistência da personalidade, memórias e perfis de usuários
    """
    
    def __init__(self):
        self.logger = get_logger('state_manager')
        self.lock = threading.RLock()
        
        # Estado principal do Kairo
        self.kairo_state = {
            "personality_traits": PERSONALITY_CONFIG["initial_traits"].copy(),
            "emotional_state": EMOTION_CONFIG["default_values"].copy(),
            "memories": [],
            "learned_patterns": {},
            "interaction_count": 0,
            "birth_time": None,
            "last_interaction": None,
            "version": "1.0"
        }
        
        # Perfil do usuário atual
        self.current_user_id = "default_user"
        self.user_profiles = {}
        
        # Cache de memórias importantes
        self.important_memories = []
        
        # Flags de controle
        self.auto_save_enabled = True
        self.last_save_time = time.time()
    
    def initialize(self):
        """Inicializa o gerenciador de estado"""
        try:
            self.logger.info("Inicializando StateManager...")
            
            # Cria diretórios necessários
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            PROFILES_DIR.mkdir(parents=True, exist_ok=True)
            
            # Carrega estado existente ou cria novo
            self._load_kairo_state()
            self._load_user_profiles()
            
            # Inicia auto-save se habilitado
            if self.auto_save_enabled:
                self._start_auto_save()
            
            log_system_event("state_manager_initialized", f"Kairo age: {self.get_kairo_age_hours():.1f}h")
            self.logger.info("StateManager inicializado com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar StateManager: {e}")
            raise
    
    def _load_kairo_state(self):
        """Carrega o estado do Kairo do arquivo"""
        state_file = DATA_DIR / "kairo_state.json"
        
        try:
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                
                # Merge com estado padrão para garantir compatibilidade
                self.kairo_state.update(loaded_state)
                
                # Valida e corrige valores se necessário
                self._validate_and_fix_state()
                
                self.logger.info(f"Estado do Kairo carregado: {len(self.kairo_state['memories'])} memórias")
            else:
                # Primeiro boot - define tempo de nascimento
                self.kairo_state["birth_time"] = datetime.now().isoformat()
                self.logger.info("Primeiro boot do Kairo - estado inicial criado")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar estado do Kairo: {e}")
            # Em caso de erro, usa estado padrão
            self.kairo_state["birth_time"] = datetime.now().isoformat()
    
    def _load_user_profiles(self):
        """Carrega perfis de usuários"""
        try:
            for profile_file in PROFILES_DIR.glob("*.json"):
                user_id = profile_file.stem
                
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile = json.load(f)
                
                self.user_profiles[user_id] = profile
                self.logger.debug(f"Perfil carregado: {user_id}")
            
            self.logger.info(f"{len(self.user_profiles)} perfis de usuário carregados")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar perfis: {e}")
    
    def _validate_and_fix_state(self):
        """Valida e corrige o estado do Kairo se necessário"""
        # Valida traços de personalidade
        trait_bounds = PERSONALITY_CONFIG["trait_bounds"]
        for trait, value in self.kairo_state["personality_traits"].items():
            if not (trait_bounds[0] <= value <= trait_bounds[1]):
                self.kairo_state["personality_traits"][trait] = 5.0
                self.logger.warning(f"Trait {trait} corrigido para valor padrão")
        
        # Valida estado emocional
        emotion_bounds = EMOTION_CONFIG["bounds"]
        for emotion, value in self.kairo_state["emotional_state"].items():
            if not (emotion_bounds[0] <= value <= emotion_bounds[1]):
                self.kairo_state["emotional_state"][emotion] = EMOTION_CONFIG["default_values"].get(emotion, 0.0)
                self.logger.warning(f"Emotion {emotion} corrigida para valor padrão")
        
        # Garante que campos obrigatórios existem
        if "birth_time" not in self.kairo_state:
            self.kairo_state["birth_time"] = datetime.now().isoformat()
        
        if "interaction_count" not in self.kairo_state:
            self.kairo_state["interaction_count"] = 0
    
    def save_state(self):
        """Salva o estado atual do Kairo"""
        with self.lock:
            try:
                state_file = DATA_DIR / "kairo_state.json"
                
                # Backup do arquivo anterior
                if state_file.exists():
                    backup_file = DATA_DIR / f"kairo_state_backup_{int(time.time())}.json"
                    state_file.rename(backup_file)
                    
                    # Mantém apenas os 5 backups mais recentes
                    backups = sorted(DATA_DIR.glob("kairo_state_backup_*.json"))
                    for old_backup in backups[:-5]:
                        old_backup.unlink()
                
                # Salva estado atual
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(self.kairo_state, f, indent=2, ensure_ascii=False)
                
                self.last_save_time = time.time()
                self.logger.debug("Estado do Kairo salvo com sucesso")
                
            except Exception as e:
                self.logger.error(f"Erro ao salvar estado: {e}")
    
    def save_user_profile(self, user_id: str):
        """Salva perfil de um usuário específico"""
        if user_id not in self.user_profiles:
            return
        
        try:
            profile_file = PROFILES_DIR / f"{user_id}.json"
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_profiles[user_id], f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Perfil do usuário {user_id} salvo")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar perfil {user_id}: {e}")
    
    def add_interaction(self, author: str, content: str, metadata: Optional[Dict] = None):
        """Adiciona uma interação à memória"""
        with self.lock:
            interaction = {
                "id": f"{int(time.time() * 1000)}_{len(self.kairo_state['memories'])}",
                "timestamp": datetime.now().isoformat(),
                "author": author,
                "content": content,
                "metadata": metadata or {},
                "importance": self._calculate_importance(content, author)
            }
            
            self.kairo_state["memories"].append(interaction)
            self.kairo_state["interaction_count"] += 1
            self.kairo_state["last_interaction"] = interaction["timestamp"]
            
            # Atualiza cache de memórias importantes
            if interaction["importance"] >= MEMORY_CONFIG["importance_threshold"]:
                self.important_memories.append(interaction)
            
            # Limita tamanho da memória
            max_memories = MEMORY_CONFIG["max_conversation_history"]
            if len(self.kairo_state["memories"]) > max_memories:
                # Remove memórias antigas menos importantes
                self._consolidate_memories()
            
            self.logger.debug(f"Interação adicionada: {author} - importance: {interaction['importance']:.2f}")
            
            return interaction
    
    def _calculate_importance(self, content: str, author: str) -> float:
        """Calcula a importância de uma interação"""
        importance = 0.5  # Base
        
        # Fatores que aumentam importância
        if len(content) > 100:  # Mensagens longas
            importance += 0.2
        
        if any(word in content.lower() for word in ["aprendi", "entendi", "interessante", "obrigado"]):
            importance += 0.3
        
        if author == "user":  # Input do usuário é mais importante
            importance += 0.1
        
        # Perguntas são importantes
        if "?" in content:
            importance += 0.2
        
        # Emocional
        emotional_words = ["amo", "odeio", "feliz", "triste", "raiva", "medo"]
        if any(word in content.lower() for word in emotional_words):
            importance += 0.3
        
        return min(1.0, importance)
    
    def _consolidate_memories(self):
        """Consolida memórias antigas, mantendo apenas as importantes"""
        memories = self.kairo_state["memories"]
        
        # Separa memórias por importância
        important = [m for m in memories if m["importance"] >= MEMORY_CONFIG["importance_threshold"]]
        recent = memories[-100:]  # Mantém as 100 mais recentes
        
        # Combina e remove duplicatas
        consolidated = []
        seen_ids = set()
        
        for memory in important + recent:
            if memory["id"] not in seen_ids:
                consolidated.append(memory)
                seen_ids.add(memory["id"])
        
        # Ordena por timestamp
        consolidated.sort(key=lambda x: x["timestamp"])
        
        removed_count = len(memories) - len(consolidated)
        self.kairo_state["memories"] = consolidated
        
        if removed_count > 0:
            log_memory_consolidation(len(memories), removed_count)
            self.logger.info(f"Memórias consolidadas: {removed_count} removidas, {len(consolidated)} mantidas")
    
    def get_personality_trait(self, trait: str) -> float:
        """Obtém valor de um traço de personalidade"""
        return self.kairo_state["personality_traits"].get(trait, 5.0)
    
    def update_personality_trait(self, trait: str, delta: float, reason: str = ""):
        """Atualiza um traço de personalidade"""
        with self.lock:
            old_value = self.kairo_state["personality_traits"].get(trait, 5.0)
            new_value = old_value + delta
            
            # Aplica limites
            trait_bounds = PERSONALITY_CONFIG["trait_bounds"]
            new_value = max(trait_bounds[0], min(trait_bounds[1], new_value))
            
            if abs(new_value - old_value) > 0.01:  # Mudança significativa
                self.kairo_state["personality_traits"][trait] = new_value
                
                from modules.logger import log_personality_change
                log_personality_change(trait, old_value, new_value, reason)
                
                self.logger.info(f"Personality trait updated: {trait} {old_value:.2f} -> {new_value:.2f}")
    
    def get_emotional_state(self) -> Dict[str, float]:
        """Obtém estado emocional atual"""
        return self.kairo_state["emotional_state"].copy()
    
    def update_emotional_state(self, emotion: str, delta: float, trigger: str = ""):
        """Atualiza uma emoção"""
        with self.lock:
            old_value = self.kairo_state["emotional_state"].get(emotion, 0.0)
            new_value = old_value + delta
            
            # Aplica limites
            emotion_bounds = EMOTION_CONFIG["bounds"]
            new_value = max(emotion_bounds[0], min(emotion_bounds[1], new_value))
            
            # Filtro anti-spam: só atualiza mudanças significativas (>= 0.5)
            change = abs(new_value - old_value)
            if change >= 0.5:
                self.kairo_state["emotional_state"][emotion] = new_value
                
                # Controle de spam temporal - só loga se passou tempo suficiente
                import time
                current_time = time.time()
                last_log_key = f"last_emotion_log_{emotion}"
                
                if not hasattr(self, '_emotion_log_times'):
                    self._emotion_log_times = {}
                
                last_log_time = self._emotion_log_times.get(last_log_key, 0)
                
                # Só loga se passou pelo menos 3 segundos desde a última mudança desta emoção
                if current_time - last_log_time >= 3.0:
                    from modules.logger import log_emotion_change
                    log_emotion_change(emotion, old_value, new_value, trigger)
                    self._emotion_log_times[last_log_key] = current_time
                
                self.logger.debug(f"Emotion updated: {emotion} {old_value:.2f} -> {new_value:.2f}")
            elif change > 0.01:
                # Atualiza valor mas não loga (mudança pequena)
                self.kairo_state["emotional_state"][emotion] = new_value
    
    def get_recent_memories(self, count: int = 10) -> List[Dict]:
        """Obtém memórias recentes"""
        return self.kairo_state["memories"][-count:]
    
    def get_important_memories(self, count: int = 20) -> List[Dict]:
        """Obtém memórias importantes"""
        important = [m for m in self.kairo_state["memories"] 
                    if m["importance"] >= MEMORY_CONFIG["importance_threshold"]]
        return important[-count:]
    
    def add_memory(self, content: str, memory_type: str = "interaction", user_id: str = "default_user"):
        """Adiciona uma nova memória com detecção de informações importantes"""
        with self.lock:
            # Detecta informações importantes no conteúdo
            importance = self._calculate_importance(content, memory_type)
            extracted_info = self._extract_important_info(content)
            
            memory = {
                "id": f"mem_{int(time.time() * 1000)}_{len(self.kairo_state['memories'])}",
                "timestamp": time.time(),
                "content": content,
                "type": memory_type,
                "importance": importance,
                "user_id": user_id,
                "extracted_info": extracted_info
            }
            
            self.kairo_state["memories"].append(memory)
            
            # Se detectou informações importantes, atualiza perfil do usuário
            if extracted_info:
                self._update_user_profile_from_info(user_id, extracted_info)
            
            # Limita número de memórias
            max_memories = MEMORY_CONFIG.get("max_memories", 1000)
            if len(self.kairo_state["memories"]) > max_memories:
                self.kairo_state["memories"] = self.kairo_state["memories"][-max_memories:]
            
            self.logger.debug(f"Memory added: importance={importance:.2f}, info={extracted_info}")
            return memory["id"]
    
    def _extract_important_info(self, content: str) -> Dict[str, Any]:
        """Extrai informações importantes do texto"""
        import re
        extracted = {}
        
        # Detecta nomes próprios
        name_patterns = [
            r"(?:meu nome é|eu sou|me chamo|sou o|sou a)\s+([A-Z][a-zA-Z\s]+)",
            r"(?:nome|chamam|chamo)(?:\s+de)?\s+([A-Z][a-zA-Z\s]+)",
            r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:é meu nome|sou eu)"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 1 and len(name) < 50:  # Nome válido
                    extracted["name"] = name
                    break
        
        # Detecta idade
        age_pattern = r"(?:tenho|idade|anos?)\s+(\d{1,3})\s*(?:anos?|de idade)"
        age_match = re.search(age_pattern, content, re.IGNORECASE)
        if age_match:
            age = int(age_match.group(1))
            if 1 <= age <= 120:
                extracted["age"] = age
        
        return extracted
    
    def _update_user_profile_from_info(self, user_id: str, extracted_info: Dict[str, Any]):
        """Atualiza perfil do usuário com informações extraídas"""
        profile = self.get_user_profile(user_id)
        
        # Atualiza informações conhecidas
        for key, value in extracted_info.items():
            if key == "name" and not profile.get("name"):
                profile["name"] = value
                self.logger.info(f"User name learned: {user_id} -> {value}")
            elif key not in profile.get("known_info", {}):
                if "known_info" not in profile:
                    profile["known_info"] = {}
                profile["known_info"][key] = value
                self.logger.info(f"User info learned: {user_id} - {key}: {value}")
        
        # Salva perfil atualizado
        self.save_user_profile(user_id)
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Obtém perfil de um usuário"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "id": user_id,
                "name": None,
                "preferences": {},
                "facts": [],
                "interaction_history": [],
                "created_at": datetime.now().isoformat()
            }
        
        return self.user_profiles[user_id]
    
    def update_user_profile(self, user_id: str, field: str, value: Any):
        """Atualiza campo do perfil do usuário"""
        profile = self.get_user_profile(user_id)
        profile[field] = value
        self.save_user_profile(user_id)
        
        self.logger.debug(f"User profile updated: {user_id}.{field} = {value}")
    
    def add_user_fact(self, user_id: str, fact: str):
        """Adiciona um fato sobre o usuário"""
        profile = self.get_user_profile(user_id)
        
        if fact not in profile["facts"]:
            profile["facts"].append(fact)
            self.save_user_profile(user_id)
            
            self.logger.info(f"User fact added: {user_id} - {fact}")
    
    def get_current_user_id(self) -> str:
        """Obtém ID do usuário atual"""
        return self.current_user_id
    
    def set_current_user(self, user_id: str):
        """Define usuário atual"""
        self.current_user_id = user_id
        self.logger.info(f"Current user set to: {user_id}")
    
    def get_kairo_age_hours(self) -> float:
        """Obtém idade do Kairo em horas"""
        if not self.kairo_state.get("birth_time"):
            return 0.0
        
        birth = datetime.fromisoformat(self.kairo_state["birth_time"])
        age = datetime.now() - birth
        return age.total_seconds() / 3600
    
    def get_interaction_count(self) -> int:
        """Obtém número total de interações"""
        return self.kairo_state["interaction_count"]
    
    def get_state_summary(self) -> Dict:
        """Obtém resumo do estado atual"""
        return {
            "kairo_age_hours": self.get_kairo_age_hours(),
            "interaction_count": self.get_interaction_count(),
            "memory_count": len(self.kairo_state["memories"]),
            "important_memories": len(self.important_memories),
            "personality_traits": self.kairo_state["personality_traits"].copy(),
            "emotional_state": self.kairo_state["emotional_state"].copy(),
            "user_profiles": len(self.user_profiles),
            "current_user": self.current_user_id
        }
    
    def _start_auto_save(self):
        """Inicia auto-save em thread separada"""
        def auto_save_loop():
            while self.auto_save_enabled:
                try:
                    time.sleep(MEMORY_CONFIG["auto_save_interval"])
                    
                    if time.time() - self.last_save_time > MEMORY_CONFIG["auto_save_interval"]:
                        self.save_state()
                        
                except Exception as e:
                    self.logger.error(f"Erro no auto-save: {e}")
        
        auto_save_thread = threading.Thread(target=auto_save_loop, daemon=True)
        auto_save_thread.start()
        
        self.logger.info("Auto-save iniciado")
    
    def shutdown(self):
        """Encerra o gerenciador de estado"""
        self.auto_save_enabled = False
        self.save_state()
        
        # Salva todos os perfis
        for user_id in self.user_profiles:
            self.save_user_profile(user_id)
        
        self.logger.info("StateManager encerrado")

if __name__ == "__main__":
    # Teste do StateManager
    sm = StateManager()
    sm.initialize()
    
    # Testa funcionalidades básicas
    sm.add_interaction("user", "Olá, meu nome é Carlos")
    sm.update_personality_trait("curiosity", 0.5, "user introduced themselves")
    sm.update_emotional_state("interest", 1.0, "new user interaction")
    
    print("Estado atual:", sm.get_state_summary())
    
    sm.shutdown()

