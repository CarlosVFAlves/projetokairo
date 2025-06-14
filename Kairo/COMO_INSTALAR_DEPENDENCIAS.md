# 🔧 COMO INSTALAR AS DEPENDÊNCIAS - PROJETO KAIRO

## ❌ PROBLEMA
Erro: `No module named 'requests'`

## ✅ SOLUÇÃO SIMPLES

### **PASSO 1: Abrir Terminal/Prompt**
- **Windows:** Pressione `Win + R`, digite `cmd`, pressione Enter
- **Mac/Linux:** Abra o Terminal

### **PASSO 2: Navegar até a pasta do projeto**
```bash
cd C:\Users\Brancarlo\Downloads\kairo_projeto_final_corrigido\kairo
```
*(Ajuste o caminho conforme onde você extraiu o projeto)*

### **PASSO 3: Instalar dependências**
```bash
pip install requests colorama
```

**OU instalar tudo de uma vez:**
```bash
pip install -r requirements.txt
```

### **PASSO 4: Testar novamente**
```bash
cd maestro
python verificacao_completa.py
```

## 🚀 COMANDOS COMPLETOS (COPIE E COLE)

**Para Windows:**
```cmd
cd C:\Users\Brancarlo\Downloads\kairo_projeto_final_corrigido\kairo
pip install requests colorama
cd maestro
python verificacao_completa.py
```

**Se der erro de permissão, use:**
```cmd
pip install --user requests colorama
```

## 📋 DEPENDÊNCIAS NECESSÁRIAS

**Essenciais (mínimas):**
- `requests` - Para comunicação com Ollama
- `colorama` - Para cores no terminal

**Opcionais (melhoram a experiência):**
- `psutil` - Monitoramento do sistema
- `nltk` - Processamento de texto avançado
- `loguru` - Logging melhorado

## ⚠️ PROBLEMAS COMUNS

### **"pip não é reconhecido"**
**Solução:** Instale Python corretamente ou use:
```cmd
python -m pip install requests colorama
```

### **"Permission denied"**
**Solução:** Use `--user`:
```cmd
pip install --user requests colorama
```

### **Python não encontrado**
**Solução:** Baixe Python em: https://python.org/downloads/
- ✅ Marque "Add Python to PATH" durante instalação

## 🎯 APÓS INSTALAR

1. **Teste o sistema:**
```bash
cd maestro
python verificacao_completa.py
```

2. **Se tudo OK, execute o Kairo:**
```bash
python main.py
```

## 📞 SE AINDA DER ERRO

Envie uma foto/print do erro que aparece após executar:
```bash
pip install requests colorama
```

Vou te ajudar a resolver! 😊

