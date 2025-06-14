#!/usr/bin/env python3
"""
test_maestro.py
Script de teste para o Sistema Maestro
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando imports dos módulos...")
    
    try:
        from config import MAESTRO_CONFIG, OLLAMA_CONFIG
        print("✅ config.py")
        
        from modules.logger import get_logger, setup_logging
        print("✅ modules.logger")
        
        from modules.state_manager import StateManager
        print("✅ modules.state_manager")
        
        from modules.emotion_engine import EmotionEngine
        print("✅ modules.emotion_engine")
        
        from modules.personality_core import PersonalityCore
        print("✅ modules.personality_core")
        
        from modules.prompt_engine import PromptEngine
        print("✅ modules.prompt_engine")
        
        from modules.ollama_client import OllamaClient
        print("✅ modules.ollama_client")
        
        from modules.action_executor import ActionExecutor
        print("✅ modules.action_executor")
        
        from modules.idle_processor import IdleProcessor
        print("✅ modules.idle_processor")
        
        from executors.base_executor import BaseExecutor
        print("✅ executors.base_executor")
        
        from executors.cli_executor import CLIExecutor
        print("✅ executors.cli_executor")
        
        from main import MaestroSystem
        print("✅ main.MaestroSystem")
        
        print("\n🎉 Todos os módulos importados com sucesso!")
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_state_manager():
    """Testa o StateManager"""
    print("\n🧠 Testando StateManager...")
    
    try:
        from modules.state_manager import StateManager
        
        sm = StateManager()
        sm.initialize()
        
        # Testa funcionalidades básicas
        sm.add_interaction("user", "Olá, teste!")
        sm.update_personality_trait("curiosity", 0.5, "teste")
        sm.update_emotional_state("joy", 1.0, "teste")
        
        # Verifica estado
        summary = sm.get_state_summary()
        print(f"✅ Estado: {summary['interaction_count']} interações, {summary['memory_count']} memórias")
        
        sm.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro no StateManager: {e}")
        return False

def test_emotion_engine():
    """Testa o EmotionEngine"""
    print("\n😊 Testando EmotionEngine...")
    
    try:
        from modules.state_manager import StateManager
        from modules.emotion_engine import EmotionEngine
        
        sm = StateManager()
        sm.initialize()
        
        ee = EmotionEngine(sm)
        ee.initialize()
        
        # Testa análise de texto
        adjustments = ee.analyze_text("Estou muito feliz hoje!")
        print(f"✅ Análise emocional: {adjustments}")
        
        # Testa estado emocional
        dominant = ee.get_dominant_emotion()
        print(f"✅ Emoção dominante: {dominant}")
        
        ee.shutdown()
        sm.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro no EmotionEngine: {e}")
        return False

def test_cli_executor():
    """Testa o CLIExecutor"""
    print("\n💻 Testando CLIExecutor...")
    
    try:
        from executors.cli_executor import CLIExecutor
        
        cli = CLIExecutor()
        cli.initialize()
        
        # Testa ações básicas
        actions = cli.get_available_actions()
        print(f"✅ {len(actions)} ações disponíveis")
        
        # Testa execução de ação
        success = cli.execute_action("speak", {"text": "Teste do CLI!"})
        print(f"✅ Ação executada: {success}")
        
        stats = cli.get_stats()
        print(f"✅ Estatísticas: {stats['total_actions']} ações")
        
        cli.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro no CLIExecutor: {e}")
        return False

def test_prompt_engine():
    """Testa o PromptEngine"""
    print("\n📝 Testando PromptEngine...")
    
    try:
        from modules.state_manager import StateManager
        from modules.emotion_engine import EmotionEngine
        from modules.personality_core import PersonalityCore
        from modules.prompt_engine import PromptEngine
        
        sm = StateManager()
        sm.initialize()
        
        ee = EmotionEngine(sm)
        ee.initialize()
        
        pc = PersonalityCore(sm, ee)
        pc.initialize()
        
        pe = PromptEngine(sm, ee, pc)
        pe.initialize()
        
        # Testa geração de prompt
        prompt = pe.generate_prompt("Olá!")
        print(f"✅ Prompt gerado: {len(prompt)} caracteres")
        
        # Testa validação
        valid_response = '{"internal_monologue": "teste", "actions": [{"command": "speak", "parameter": "oi"}]}'
        is_valid = pe.validate_response(valid_response)
        print(f"✅ Validação de resposta: {is_valid}")
        
        pc.shutdown()
        ee.shutdown()
        sm.shutdown()
        return True
        
    except Exception as e:
        print(f"❌ Erro no PromptEngine: {e}")
        return False

def test_file_structure():
    """Verifica estrutura de arquivos"""
    print("\n📁 Verificando estrutura de arquivos...")
    
    required_files = [
        "config.py",
        "main.py",
        "modules/__init__.py",
        "modules/logger.py",
        "modules/state_manager.py",
        "modules/emotion_engine.py",
        "modules/personality_core.py",
        "modules/prompt_engine.py",
        "modules/ollama_client.py",
        "modules/action_executor.py",
        "modules/idle_processor.py",
        "executors/__init__.py",
        "executors/base_executor.py",
        "executors/cli_executor.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Arquivos faltando: {missing_files}")
        return False
    else:
        print("\n🎉 Todos os arquivos necessários estão presentes!")
        return True

def main():
    """Função principal de teste"""
    print("🤖 TESTE DO SISTEMA MAESTRO")
    print("=" * 50)
    
    tests = [
        ("Estrutura de arquivos", test_file_structure),
        ("Imports", test_imports),
        ("StateManager", test_state_manager),
        ("EmotionEngine", test_emotion_engine),
        ("CLIExecutor", test_cli_executor),
        ("PromptEngine", test_prompt_engine)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} falhou")
        except Exception as e:
            print(f"❌ {test_name} falhou com erro: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("\n🚀 O Sistema Maestro está pronto para uso!")
        print("\nPara executar:")
        print("  python main.py")
        print("\nNota: Certifique-se de que o Ollama está rodando localmente")
        return 0
    else:
        print("❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

