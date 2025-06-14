#!/usr/bin/env python3
"""
test_main_quick.py
Teste rápido do main.py para verificar se inicializa sem erros
"""

import sys
import time
import threading
from pathlib import Path

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

def test_main_initialization():
    """Testa se o main.py inicializa sem erros críticos"""
    try:
        from main import MaestroSystem
        
        print("🔍 Testando inicialização do sistema principal...")
        
        # Cria sistema
        maestro = MaestroSystem()
        
        # Tenta inicializar (sem Ollama, vai dar warning mas não erro crítico)
        success = maestro.initialize("cli")
        
        if success:
            print("✅ Sistema inicializado com sucesso!")
            print("ℹ️  Nota: Warnings sobre Ollama são normais se não estiver rodando")
            
            # Encerra rapidamente
            maestro.shutdown()
            return True
        else:
            print("❌ Falha na inicialização")
            return False
            
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return False

if __name__ == "__main__":
    success = test_main_initialization()
    if success:
        print("\n🎉 SISTEMA PRINCIPAL FUNCIONANDO!")
        print("📝 Para usar: python main.py")
        print("⚠️  Lembre-se de iniciar o Ollama primeiro: ollama serve")
    else:
        print("\n❌ SISTEMA COM PROBLEMAS")
    
    sys.exit(0 if success else 1)

