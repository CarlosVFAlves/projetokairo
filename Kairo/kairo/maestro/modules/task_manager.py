"""
task_manager.py
Gerenciador de Tarefas e Objetivos para o Kairo
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any

from modules.logger import get_logger
from config import DATA_DIR

class TaskManager:
    """
    Gerencia os objetivos de longo prazo e as tarefas do Kairo.
    Permite que a IA tenha uma lista de "coisas a fazer" que pode ser
    processada durante os momentos de ociosidade.
    """

    def __init__(self):
        self.logger = get_logger('task_manager')
        self.tasks_file_path = DATA_DIR / "tasks.json"
        self.tasks: List[Dict[str, Any]] = []

    def initialize(self):
        """Inicializa o TaskManager, carregando as tarefas existentes."""
        self.logger.info("Inicializando TaskManager...")
        self._load_tasks()
        self.logger.info(f"{len(self.tasks)} tarefas carregadas. {self.get_pending_tasks_count()} pendentes.")
        self.logger.info("TaskManager inicializado com sucesso.")

    def _load_tasks(self):
        """Carrega a lista de tarefas do arquivo JSON."""
        try:
            if self.tasks_file_path.exists():
                with open(self.tasks_file_path, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
            else:
                self.logger.info("Arquivo de tarefas não encontrado. Começando com uma lista vazia.")
                self.tasks = []
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar o arquivo de tarefas: {self.tasks_file_path}. Criando um novo arquivo.")
            self.tasks = []
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar tarefas: {e}")
            self.tasks = []

    def _save_tasks(self):
        """Salva a lista de tarefas atual no arquivo JSON."""
        try:
            with open(self.tasks_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erro ao salvar tarefas: {e}")

    def add_goal(self, goal_description: str) -> Optional[Dict[str, Any]]:
        """
        Adiciona um novo objetivo de alto nível à lista de tarefas.
        Por enquanto, um objetivo é tratado como uma única tarefa.
        """
        if not goal_description or not isinstance(goal_description, str):
            self.logger.warning("Tentativa de adicionar um objetivo inválido.")
            return None

        task_id = str(uuid.uuid4())
        new_task = {
            "id": task_id,
            "goal": goal_description,
            "status": "pending",
            "subtasks": [], # Para o futuro
            "result": None,
            "created_at": self._get_timestamp(),
            "completed_at": None
        }

        self.tasks.append(new_task)
        self._save_tasks()
        self.logger.info(f"Novo objetivo adicionado com ID {task_id}: '{goal_description}'")
        return new_task

    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """
        Retorna a próxima tarefa pendente da lista.
        A lógica de priorização pode ser adicionada aqui no futuro.
        """
        for task in self.tasks:
            if task.get("status") == "pending":
                self.logger.info(f"Próxima tarefa encontrada: {task.get('id')}")
                return task

        self.logger.info("Nenhuma tarefa pendente encontrada.")
        return None

    def mark_task_complete(self, task_id: str, result: str) -> bool:
        """
        Marca uma tarefa como concluída.
        """
        for task in self.tasks:
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["result"] = result
                task["completed_at"] = self._get_timestamp()
                self._save_tasks()
                self.logger.info(f"Tarefa {task_id} marcada como concluída.")
                return True

        self.logger.warning(f"Tentativa de completar tarefa não encontrada com ID: {task_id}")
        return False

    def get_pending_tasks_count(self) -> int:
        """Retorna o número de tarefas pendentes."""
        return len([task for task in self.tasks if task.get("status") == "pending"])

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Retorna todas as tarefas."""
        return self.tasks

    def _get_timestamp(self) -> str:
        """Retorna um timestamp no formato ISO."""
        from datetime import datetime
        return datetime.now().isoformat()

    def shutdown(self):
        """Encerra o TaskManager."""
        self.logger.info("TaskManager encerrado.")

if __name__ == "__main__":
    # Teste rápido do TaskManager
    print("--- Testando TaskManager ---")

    # Garante que o diretório de dados exista
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    tm = TaskManager()
    tm.initialize()

    print(f"Tarefas pendentes no início: {tm.get_pending_tasks_count()}")

    # Adiciona um novo objetivo
    new_goal = tm.add_goal("Escrever um poema sobre a chuva.")
    if new_goal:
        print(f"Novo objetivo adicionado: {new_goal['id']}")

    print(f"Tarefas pendentes agora: {tm.get_pending_tasks_count()}")

    # Pega a próxima tarefa
    next_task = tm.get_next_task()
    if next_task:
        print(f"Próxima tarefa a ser executada: {next_task['goal']}")

        # Marca como concluída
        tm.mark_task_complete(next_task['id'], "Poema concluído com sucesso.")

    print(f"Tarefas pendentes no final: {tm.get_pending_tasks_count()}")

    # Limpa o arquivo de teste
    if tm.tasks_file_path.exists():
        tm.tasks_file_path.unlink()
        print("Arquivo de tarefas de teste removido.")

    tm.shutdown()
    print("--- Teste do TaskManager concluído ---")
