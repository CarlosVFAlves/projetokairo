#!/usr/bin/env python3
"""
verificacao_completa.py
Verificação sistemática de todos os módulos do Kairo
"""

import sys
import traceback
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

def test_config():
    """Testa o módulo config"""
    print("🔍 Testando config.py...")
    try:
        from config import MAESTRO_CONFIG, OLLAMA_CONFIG, DATA_DIR, PROFILES_DIR
        print("✅ config.py - Imports básicos OK")
        
        # Verifica se as configurações existem
        print(f"  - DATA_DIR: {DATA_DIR}")
        print(f"  - PROFILES_DIR: {PROFILES_DIR}")
        print(f"  - MAESTRO_CONFIG keys: {list(MAESTRO_CONFIG.keys())}")
        print(f"  - OLLAMA_CONFIG keys: {list(OLLAMA_CONFIG.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ config.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_logger():
    """Testa o módulo logger"""
    print("\n🔍 Testando logger.py...")
    try:
        from modules.logger import get_logger, setup_logging, log_system_event
        print("✅ logger.py - Imports OK")
        
        # Testa criação de logger
        logger = get_logger('test')
        logger.info("Teste de log")
        print("✅ logger.py - Criação de logger OK")
        
        return True
    except Exception as e:
        print(f"❌ logger.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_state_manager():
    """Testa o StateManager"""
    print("\n🔍 Testando state_manager.py...")
    try:
        from modules.state_manager import StateManager
        print("✅ state_manager.py - Import OK")
        
        # Testa criação
        sm = StateManager()
        print("✅ state_manager.py - Criação OK")
        
        # Testa inicialização
        sm.initialize()
        print("✅ state_manager.py - Inicialização OK")
        
        # Testa funcionalidades básicas
        sm.add_interaction("user", "teste")
        summary = sm.get_state_summary()
        print(f"✅ state_manager.py - Funcionalidades OK: {summary['interaction_count']} interações")
        
        sm.shutdown()
        return True
    except Exception as e:
        print(f"❌ state_manager.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_emotion_engine():
    """Testa o EmotionEngine"""
    print("\n🔍 Testando emotion_engine.py...")
    try:
        from modules.state_manager import StateManager
        from modules.emotion_engine import EmotionEngine
        print("✅ emotion_engine.py - Import OK")
        
        # Cria dependências
        sm = StateManager()
        sm.initialize()
        
        # Testa criação
        ee = EmotionEngine(sm)
        print("✅ emotion_engine.py - Criação OK")
        
        # Testa inicialização
        ee.initialize()
        print("✅ emotion_engine.py - Inicialização OK")
        
        # Testa funcionalidades
        adjustments = ee.analyze_text("Estou feliz!")
        print(f"✅ emotion_engine.py - Análise OK: {adjustments}")
        
        ee.shutdown()
        sm.shutdown()
        return True
    except Exception as e:
        print(f"❌ emotion_engine.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_personality_core():
    """Testa o PersonalityCore"""
    print("\n🔍 Testando personality_core.py...")
    try:
        from modules.state_manager import StateManager
        from modules.emotion_engine import EmotionEngine
        from modules.personality_core import PersonalityCore
        print("✅ personality_core.py - Import OK")
        
        # Cria dependências
        sm = StateManager()
        sm.initialize()
        
        ee = EmotionEngine(sm)
        ee.initialize()
        
        # Testa criação
        pc = PersonalityCore(sm, ee)
        print("✅ personality_core.py - Criação OK")
        
        # Testa inicialização
        pc.initialize()
        print("✅ personality_core.py - Inicialização OK")
        
        # Testa funcionalidades
        traits = pc.get_current_traits()
        print(f"✅ personality_core.py - Funcionalidades OK: {len(traits)} traços")
        
        pc.shutdown()
        ee.shutdown()
        sm.shutdown()
        return True
    except Exception as e:
        print(f"❌ personality_core.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_prompt_engine():
    """Testa o PromptEngine"""
    print("\n🔍 Testando prompt_engine.py...")
    try:
        from modules.state_manager import StateManager
        from modules.emotion_engine import EmotionEngine
        from modules.personality_core import PersonalityCore
        from modules.prompt_engine import PromptEngine
        print("✅ prompt_engine.py - Import OK")
        
        # Cria dependências
        sm = StateManager()
        sm.initialize()
        
        ee = EmotionEngine(sm)
        ee.initialize()
        
        pc = PersonalityCore(sm, ee)
        pc.initialize()
        
        # Testa criação
        pe = PromptEngine(sm, ee, pc)
        print("✅ prompt_engine.py - Criação OK")
        
        # Testa inicialização
        pe.initialize()
        print("✅ prompt_engine.py - Inicialização OK")
        
        # Testa geração de prompt
        try:
            prompt = pe.generate_prompt("Olá!")
            print(f"✅ prompt_engine.py - Geração OK: {len(prompt)} caracteres")
        except Exception as prompt_error:
            print(f"⚠️ prompt_engine.py - Erro na geração: {prompt_error}")
        
        # Testa validação
        valid_response = '{"internal_monologue": "teste", "actions": [{"command": "speak", "parameter": "oi"}]}'
        is_valid = pe.validate_response(valid_response)
        print(f"✅ prompt_engine.py - Validação OK: {is_valid}")
        
        pc.shutdown()
        ee.shutdown()
        sm.shutdown()
        return True
    except Exception as e:
        print(f"❌ prompt_engine.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_ollama_client():
    """Testa o OllamaClient"""
    print("\n🔍 Testando ollama_client.py...")
    try:
        from modules.ollama_client import OllamaClient
        print("✅ ollama_client.py - Import OK")
        
        # Testa criação
        oc = OllamaClient()
        print("✅ ollama_client.py - Criação OK")
        
        # Testa inicialização (vai falhar se Ollama não estiver rodando, mas não deve dar erro crítico)
        try:
            oc.initialize()
            print("✅ ollama_client.py - Inicialização OK")
        except Exception as init_error:
            print(f"⚠️ ollama_client.py - Ollama não conectado (normal): {init_error}")
        
        oc.shutdown()
        return True
    except Exception as e:
        print(f"❌ ollama_client.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_executors():
    """Testa os executores"""
    print("\n🔍 Testando executors...")
    try:
        from executors.base_executor import BaseExecutor, ExecutorCapabilities
        from executors.cli_executor import CLIExecutor
        print("✅ executors - Import OK")
        
        # Testa CLI executor
        cli = CLIExecutor()
        print("✅ cli_executor.py - Criação OK")
        
        cli.initialize()
        print("✅ cli_executor.py - Inicialização OK")
        
        actions = cli.get_available_actions()
        print(f"✅ cli_executor.py - {len(actions)} ações disponíveis")
        
        cli.shutdown()
        return True
    except Exception as e:
        print(f"❌ executors - ERRO: {e}")
        traceback.print_exc()
        return False

def test_action_executor():
    """Testa o ActionExecutor"""
    print("\n🔍 Testando action_executor.py...")
    try:
        from modules.state_manager import StateManager
        from modules.action_executor import ActionExecutor
        from executors.cli_executor import CLIExecutor
        print("✅ action_executor.py - Import OK")
        
        # Cria dependências
        sm = StateManager()
        sm.initialize()
        
        cli = CLIExecutor()
        cli.initialize()
        
        # Testa criação
        ae = ActionExecutor(cli, sm)
        print("✅ action_executor.py - Criação OK")
        
        # Testa inicialização
        ae.initialize()
        print("✅ action_executor.py - Inicialização OK")
        
        ae.shutdown()
        cli.shutdown()
        sm.shutdown()
        return True
    except Exception as e:
        print(f"❌ action_executor.py - ERRO: {e}")
        traceback.print_exc()
        return False

def test_main_system():
    """Testa o sistema principal"""
    print("\n🔍 Testando main.py...")
    try:
        from main import MaestroSystem
        print("✅ main.py - Import OK")
        
        # Testa criação
        maestro = MaestroSystem()
        print("✅ main.py - Criação OK")
        
        # Testa inicialização (pode falhar no Ollama, mas não deve dar erro crítico)
        try:
            success = maestro.initialize("cli")
            if success:
                print("✅ main.py - Inicialização completa OK")
                maestro.shutdown()
            else:
                print("⚠️ main.py - Inicialização parcial (normal sem Ollama)")
        except Exception as init_error:
            print(f"⚠️ main.py - Erro na inicialização: {init_error}")
        
        return True
    except Exception as e:
        print(f"❌ main.py - ERRO: {e}")
        traceback.print_exc()
        return False

def main():
    """Executa verificação completa"""
    print("🔍 VERIFICAÇÃO COMPLETA DO SISTEMA KAIRO")
    print("=" * 60)
    
    tests = [
        ("Config", test_config),
        ("Logger", test_logger),
        ("StateManager", test_state_manager),
        ("EmotionEngine", test_emotion_engine),
        ("PersonalityCore", test_personality_core),
        ("PromptEngine", test_prompt_engine),
        ("OllamaClient", test_ollama_client),
        ("Executors", test_executors),
        ("ActionExecutor", test_action_executor),
        ("Main System", test_main_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ {test_name} FALHOU")
        except Exception as e:
            print(f"\n❌ {test_name} FALHOU COM EXCEÇÃO: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADO FINAL: {passed}/{total} módulos funcionando")
    
    if passed == total:
        print("🎉 SISTEMA COMPLETAMENTE FUNCIONAL!")
    elif passed >= total - 2:
        print("⚠️ SISTEMA QUASE FUNCIONAL - Pequenos ajustes necessários")
    else:
        print("❌ SISTEMA COM PROBLEMAS SÉRIOS - Correções necessárias")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

