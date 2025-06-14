"""
logger.py
Sistema de logging para o Maestro
"""

import logging
import logging.handlers
from pathlib import Path
from config import LOGGING_CONFIG, LOGS_DIR

class MaestroLogger:
    """Sistema de logging centralizado para o Maestro"""
    
    def __init__(self):
        self.loggers = {}
        self._setup_main_logger()
    
    def _setup_main_logger(self):
        """Configura o logger principal"""
        # Cria o diretório de logs se não existir
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configura o logger principal
        logger = logging.getLogger('maestro')
        logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
        
        # Remove handlers existentes para evitar duplicação
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Handler para arquivo com rotação
        file_handler = logging.handlers.RotatingFileHandler(
            LOGGING_CONFIG['file_path'],
            maxBytes=LOGGING_CONFIG['max_file_size'],
            backupCount=LOGGING_CONFIG['backup_count'],
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(LOGGING_CONFIG['format'])
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Adiciona handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        self.loggers['maestro'] = logger
    
    def get_logger(self, name='maestro'):
        """Obtém um logger específico"""
        if name not in self.loggers:
            logger = logging.getLogger(f'maestro.{name}')
            logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
            self.loggers[name] = logger
        
        return self.loggers[name]
    
    def log_personality_change(self, trait, old_value, new_value, reason):
        """Log específico para mudanças de personalidade"""
        logger = self.get_logger('personality')
        logger.info(f"PERSONALITY_CHANGE: {trait} {old_value:.2f} -> {new_value:.2f} (reason: {reason})")
    
    def log_emotion_change(self, emotion, old_value, new_value, trigger):
        """Log específico para mudanças emocionais"""
        logger = self.get_logger('emotions')
        logger.info(f"EMOTION_CHANGE: {emotion} {old_value:.2f} -> {new_value:.2f} (trigger: {trigger})")
    
    def log_learning_event(self, event_type, details):
        """Log específico para eventos de aprendizado"""
        logger = self.get_logger('learning')
        logger.info(f"LEARNING_EVENT: {event_type} - {details}")
    
    def log_interaction(self, user_id, message_type, content_summary):
        """Log específico para interações"""
        logger = self.get_logger('interactions')
        logger.info(f"INTERACTION: user={user_id} type={message_type} summary={content_summary}")
    
    def log_decision(self, context, decision, reasoning):
        """Log específico para decisões do Kairo"""
        logger = self.get_logger('decisions')
        logger.info(f"DECISION: context={context} decision={decision} reasoning={reasoning}")
    
    def log_memory_consolidation(self, memories_processed, insights_gained):
        """Log específico para consolidação de memória"""
        logger = self.get_logger('memory')
        logger.info(f"MEMORY_CONSOLIDATION: processed={memories_processed} insights={insights_gained}")
    
    def log_error(self, module, error, context=None):
        """Log específico para erros"""
        logger = self.get_logger('errors')
        context_str = f" context={context}" if context else ""
        logger.error(f"ERROR: module={module} error={error}{context_str}")
    
    def log_system_event(self, event, details):
        """Log específico para eventos do sistema"""
        logger = self.get_logger('system')
        logger.info(f"SYSTEM_EVENT: {event} - {details}")

# Instância global do logger
_maestro_logger = None

def get_logger(name='maestro'):
    """Função global para obter um logger"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    return _maestro_logger.get_logger(name)

def log_personality_change(trait, old_value, new_value, reason):
    """Função global para log de mudanças de personalidade"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_personality_change(trait, old_value, new_value, reason)

def log_emotion_change(emotion, old_value, new_value, trigger):
    """Função global para log de mudanças emocionais"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_emotion_change(emotion, old_value, new_value, trigger)

def log_learning_event(event_type, details):
    """Função global para log de eventos de aprendizado"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_learning_event(event_type, details)

def log_interaction(user_id, message_type, content_summary):
    """Função global para log de interações"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_interaction(user_id, message_type, content_summary)

def log_decision(context, decision, reasoning):
    """Função global para log de decisões"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_decision(context, decision, reasoning)

def log_memory_consolidation(memories_processed, insights_gained):
    """Função global para log de consolidação de memória"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_memory_consolidation(memories_processed, insights_gained)

def log_error(module, error, context=None):
    """Função global para log de erros"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_error(module, error, context)

def log_system_event(event, details):
    """Função global para log de eventos do sistema"""
    global _maestro_logger
    if _maestro_logger is None:
        _maestro_logger = MaestroLogger()
    _maestro_logger.log_system_event(event, details)

if __name__ == "__main__":
    # Teste do sistema de logging
    logger = get_logger()
    logger.info("Sistema de logging inicializado")
    
    # Testa logs específicos
    log_personality_change("curiosity", 5.0, 5.2, "user asked interesting question")
    log_emotion_change("interest", 5.0, 6.5, "engaging conversation")
    log_learning_event("pattern_recognition", "user prefers technical discussions")
    log_interaction("user_001", "question", "asked about AI consciousness")
    log_decision("conversation_style", "more_technical", "user shows technical background")
    
    print("Teste de logging concluído. Verifique o arquivo de log.")

