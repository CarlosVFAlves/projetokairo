"""
conversation_manager.py
Gerenciador de conversas e organização de arquivos
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from config import DATA_DIR
from modules.logger import get_logger

class ConversationManager:
    """Gerencia conversas e organização de arquivos"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Diretórios organizados
        self.conversations_dir = DATA_DIR / "conversations"
        self.user_profiles_dir = DATA_DIR / "user_profiles"
        self.system_logs_dir = DATA_DIR / "system_logs"
        self.backups_dir = DATA_DIR / "backups"
        
        # Cria diretórios se não existirem
        self._ensure_directories()
        
        # Conversa atual
        self.current_conversation = None
        self.conversation_start_time = None
    
    def _ensure_directories(self):
        """Garante que todos os diretórios existem"""
        for directory in [self.conversations_dir, self.user_profiles_dir, 
                         self.system_logs_dir, self.backups_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def start_new_conversation(self, user_id: str = "default_user") -> str:
        """Inicia uma nova conversa"""
        self.conversation_start_time = time.time()
        timestamp = int(self.conversation_start_time)
        
        conversation_id = f"conv_{timestamp}_{user_id}"
        
        self.current_conversation = {
            "id": conversation_id,
            "user_id": user_id,
            "start_time": self.conversation_start_time,
            "messages": [],
            "metadata": {
                "kairo_age_hours": 0,
                "total_interactions": 0,
                "emotions_triggered": [],
                "personality_changes": []
            }
        }
        
        self.logger.info(f"Nova conversa iniciada: {conversation_id}")
        return conversation_id
    
    def add_message(self, sender: str, content: str, metadata: Dict = None):
        """Adiciona mensagem à conversa atual"""
        if not self.current_conversation:
            self.start_new_conversation()
        
        message = {
            "timestamp": time.time(),
            "sender": sender,
            "content": content,
            "metadata": metadata or {}
        }
        
        self.current_conversation["messages"].append(message)
        
        # Auto-save a cada 5 mensagens
        if len(self.current_conversation["messages"]) % 5 == 0:
            self.save_current_conversation()
    
    def save_current_conversation(self) -> Optional[str]:
        """Salva a conversa atual"""
        if not self.current_conversation:
            return None
        
        conversation_id = self.current_conversation["id"]
        file_path = self.conversations_dir / f"{conversation_id}.json"
        
        try:
            # Atualiza metadados
            self.current_conversation["end_time"] = time.time()
            self.current_conversation["duration_minutes"] = (
                self.current_conversation["end_time"] - self.current_conversation["start_time"]
            ) / 60
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_conversation, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Conversa salva: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar conversa: {e}")
            return None
    
    def load_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Carrega uma conversa específica"""
        file_path = self.conversations_dir / f"{conversation_id}.json"
        
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar conversa {conversation_id}: {e}")
            return None
    
    def get_recent_conversations(self, user_id: str = None, limit: int = 10) -> List[Dict]:
        """Obtém conversas recentes"""
        conversations = []
        
        try:
            for file_path in self.conversations_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        conv = json.load(f)
                        
                    # Filtra por usuário se especificado
                    if user_id and conv.get("user_id") != user_id:
                        continue
                    
                    conversations.append({
                        "id": conv["id"],
                        "user_id": conv["user_id"],
                        "start_time": conv["start_time"],
                        "message_count": len(conv["messages"]),
                        "duration_minutes": conv.get("duration_minutes", 0)
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao ler conversa {file_path}: {e}")
                    continue
            
            # Ordena por tempo (mais recente primeiro)
            conversations.sort(key=lambda x: x["start_time"], reverse=True)
            return conversations[:limit]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter conversas recentes: {e}")
            return []
    
    def cleanup_old_conversations(self, days_to_keep: int = 30):
        """Remove conversas antigas"""
        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)
        removed_count = 0
        
        try:
            for file_path in self.conversations_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        conv = json.load(f)
                    
                    if conv.get("start_time", 0) < cutoff_time:
                        # Move para backup antes de remover
                        backup_path = self.backups_dir / file_path.name
                        file_path.rename(backup_path)
                        removed_count += 1
                        
                except Exception as e:
                    self.logger.warning(f"Erro ao processar {file_path}: {e}")
                    continue
            
            if removed_count > 0:
                self.logger.info(f"Conversas antigas movidas para backup: {removed_count}")
                
        except Exception as e:
            self.logger.error(f"Erro na limpeza de conversas: {e}")
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas das conversas"""
        try:
            total_conversations = len(list(self.conversations_dir.glob("*.json")))
            total_messages = 0
            total_duration = 0
            users = set()
            
            for file_path in self.conversations_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        conv = json.load(f)
                    
                    total_messages += len(conv["messages"])
                    total_duration += conv.get("duration_minutes", 0)
                    users.add(conv["user_id"])
                    
                except Exception:
                    continue
            
            return {
                "total_conversations": total_conversations,
                "total_messages": total_messages,
                "total_duration_hours": total_duration / 60,
                "unique_users": len(users),
                "average_messages_per_conversation": total_messages / max(total_conversations, 1),
                "average_duration_minutes": total_duration / max(total_conversations, 1)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular estatísticas: {e}")
            return {}
    
    def export_conversation_text(self, conversation_id: str) -> Optional[str]:
        """Exporta conversa como texto legível"""
        conversation = self.load_conversation(conversation_id)
        if not conversation:
            return None
        
        try:
            lines = []
            lines.append(f"=== CONVERSA {conversation_id} ===")
            lines.append(f"Usuário: {conversation['user_id']}")
            lines.append(f"Início: {datetime.fromtimestamp(conversation['start_time'])}")
            lines.append(f"Duração: {conversation.get('duration_minutes', 0):.1f} minutos")
            lines.append("=" * 50)
            lines.append("")
            
            for msg in conversation["messages"]:
                timestamp = datetime.fromtimestamp(msg["timestamp"])
                sender = "👤 Usuário" if msg["sender"] == "user" else "🤖 Kairo"
                lines.append(f"[{timestamp.strftime('%H:%M:%S')}] {sender}:")
                lines.append(msg["content"])
                lines.append("")
            
            return "\n".join(lines)
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar conversa: {e}")
            return None

