"""
config.py
Configurações globais do sistema Maestro
"""

import os
from pathlib import Path

# Caminhos base
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"
LOGS_DIR = DATA_DIR / "logs"

# Configurações do Ollama
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "llama3.2:3b",  # Modelo padrão, pode ser alterado
    "timeout": 30,
    "max_retries": 3,
    "temperature": 0.7,
    "max_tokens": 1000
}

# Configurações da OpenAI
OPENAI_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "model": "gpt-4-turbo",
    "streaming_model": "gpt-4-turbo",
    "temperature": 0.7,
    "max_tokens": 1500
}

# Configurações do sistema de personalidade evolutiva
PERSONALITY_CONFIG = {
    "learning_rate": 0.1,  # Taxa de aprendizado para mudanças de personalidade
    "trait_bounds": (0.0, 10.0),  # Limites para valores de traços
    "initial_traits": {
        # Kairo começa neutro, sem personalidade definida
        "curiosity": 5.0,
        "empathy": 5.0,
        "creativity": 5.0,
        "logic": 5.0,
        "humor": 5.0,
        "assertiveness": 5.0,
        "patience": 5.0,
        "openness": 5.0
    },
    "trait_influences": {
        # Como diferentes tipos de interação influenciam os traços
        "positive_feedback": {"empathy": 0.1, "patience": 0.1},
        "questions": {"curiosity": 0.1, "openness": 0.1},
        "creative_requests": {"creativity": 0.1, "humor": 0.05},
        "logical_discussions": {"logic": 0.1, "assertiveness": 0.05},
        "negative_feedback": {"patience": -0.05, "assertiveness": 0.05}
    }
}

# Configurações do sistema emocional
EMOTION_CONFIG = {
    "emotions": ["joy", "sadness", "anger", "fear", "surprise", "interest"],
    "default_values": {
        "joy": 5.0,
        "sadness": 0.0,
        "anger": 0.0,
        "fear": 0.0,
        "surprise": 0.0,
        "interest": 5.0
    },
    "decay_rates": {
        # Taxa de decaimento por minuto
        "joy": 0.1,
        "sadness": 0.05,
        "anger": 0.2,
        "fear": 0.15,
        "surprise": 0.3,
        "interest": 0.05
    },
    "bounds": (0.0, 10.0)
}

# Configurações de memória
MEMORY_CONFIG = {
    "max_conversation_history": 1000,
    "max_profile_facts": 100,
    "memory_consolidation_interval": 3600,  # 1 hora em segundos
    "importance_threshold": 0.7,  # Limiar para considerar uma memória importante
    "auto_save_interval": 300  # 5 minutos em segundos
}

# Configurações de ociosidade
IDLE_CONFIG = {
    "idle_timeout": 300,  # 5 minutos em segundos
    "idle_check_interval": 60,  # 1 minuto em segundos
    "max_idle_actions": 3,
    "reflection_probability": 0.3,  # Probabilidade de reflexão durante ociosidade
    "learning_probability": 0.2   # Probabilidade de consolidação de aprendizado
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": LOGS_DIR / "maestro.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Configurações do servidor de gerenciamento
MANAGER_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
    "cors_enabled": True
}

# Configurações de segurança
SECURITY_CONFIG = {
    "max_input_length": 2000,
    "rate_limit": 60,  # Máximo de mensagens por minuto
    "sanitize_input": True,
    "backup_frequency": 24 * 3600  # Backup a cada 24 horas
}

# Função para criar diretórios necessários
def ensure_directories():
    """Cria os diretórios necessários se não existirem"""
    for directory in [DATA_DIR, PROFILES_DIR, LOGS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

# Função para validar configurações
def validate_config():
    """Valida as configurações do sistema"""
    errors = []
    
    # Valida configurações de personalidade
    for trait, value in PERSONALITY_CONFIG["initial_traits"].items():
        min_val, max_val = PERSONALITY_CONFIG["trait_bounds"]
        if not (min_val <= value <= max_val):
            errors.append(f"Trait {trait} value {value} is out of bounds [{min_val}, {max_val}]")
    
    # Valida configurações emocionais
    for emotion, value in EMOTION_CONFIG["default_values"].items():
        min_val, max_val = EMOTION_CONFIG["bounds"]
        if not (min_val <= value <= max_val):
            errors.append(f"Emotion {emotion} value {value} is out of bounds [{min_val}, {max_val}]")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(errors))
    
    return True

# Inicialização
if __name__ == "__main__":
    ensure_directories()
    validate_config()
    print("Configuração validada com sucesso!")
