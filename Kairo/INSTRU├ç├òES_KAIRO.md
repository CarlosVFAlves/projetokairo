# 🤖 PROJETO KAIRO - INSTRUÇÕES DE INSTALAÇÃO E USO

## 📦 CONTEÚDO DO PACOTE

Este arquivo contém o Sistema Maestro completo do projeto Kairo - uma IA com personalidade evolutiva que funciona 100% local.

## 🔧 PRÉ-REQUISITOS

### 1. Python 3.8+
```bash
python --version  # Deve ser 3.8 ou superior
```

### 2. Ollama (LLM Local)
```bash
# Linux/Mac
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Baixe de: https://ollama.ai/download

# Instale um modelo (escolha um):
ollama pull llama2        # Modelo padrão (4GB)
ollama pull llama2:7b     # Versão 7B (4GB)
ollama pull llama2:13b    # Versão 13B (7GB)
ollama pull codellama     # Especializado em código
ollama pull mistral       # Alternativa rápida
```

## 🚀 INSTALAÇÃO

### 1. Extrair o projeto
```bash
unzip kairo_projeto_completo.zip
cd kairo/maestro
```

### 2. Verificar estrutura
```bash
# Deve mostrar:
# kairo/
# ├── maestro/           # Sistema principal
# ├── manager/           # Interface de gerenciamento (futuro)
# ├── docs/              # Documentação
# └── README.md
```

### 3. Testar instalação
```bash
python test_maestro.py
```

## ▶️ EXECUTAR O KAIRO

### 1. Iniciar Ollama (em terminal separado)
```bash
ollama serve
```

### 2. Executar Kairo
```bash
cd kairo/maestro
python main.py
```

### 3. Interagir
```
👤 Você: Olá, como você está?
🤖 Kairo: [resposta personalizada]
```

## 🎮 COMANDOS DISPONÍVEIS

Durante a conversa, você pode usar:

- `/help` - Mostra ajuda completa
- `/status` - Status do sistema e personalidade atual
- `/clear` - Limpa a tela
- `/save` - Salva a conversa atual
- `/quit` - Encerra o programa

## 🧬 CARACTERÍSTICAS ÚNICAS

### Personalidade Evolutiva
- Kairo começa neutro e desenvolve personalidade através das interações
- 8 traços: curiosity, empathy, creativity, logic, humor, assertiveness, patience, openness
- Cada conversa influencia seu desenvolvimento

### Sistema Emocional
- 6 emoções: joy, sadness, anger, fear, surprise, interest
- Emoções influenciam respostas e cores no terminal
- Decaimento natural ao longo do tempo

### Memória Persistente
- Lembra de conversas anteriores
- Consolida memórias importantes
- Perfis individuais por usuário

### Ações Proativas
- Age durante períodos de ociosidade
- Reflexões internas
- Expressão de curiosidade

## 🔧 CONFIGURAÇÃO AVANÇADA

### Modelos Ollama Recomendados

**Para máquinas potentes (16GB+ RAM):**
```bash
ollama pull llama2:13b    # Melhor qualidade
ollama pull codellama:13b # Para programação
```

**Para máquinas médias (8GB RAM):**
```bash
ollama pull llama2:7b     # Padrão recomendado
ollama pull mistral:7b    # Alternativa rápida
```

**Para máquinas básicas (4GB RAM):**
```bash
ollama pull llama2        # Versão compacta
ollama pull tinyllama     # Ultra compacto
```

### Personalizar Configurações

Edite `config.py` para ajustar:
- Taxa de aprendizado da personalidade
- Intensidade emocional
- Frequência de auto-save
- Modelos Ollama

## 🐛 SOLUÇÃO DE PROBLEMAS

### Erro: "Ollama não conectado"
```bash
# Verifique se Ollama está rodando
ollama list

# Se não estiver, inicie:
ollama serve
```

### Erro: "Modelo não encontrado"
```bash
# Liste modelos instalados
ollama list

# Instale um modelo
ollama pull llama2
```

### Erro de importação Python
```bash
# Verifique se está no diretório correto
cd kairo/maestro

# Teste imports
python test_maestro.py
```

### Performance lenta
- Use modelo menor (tinyllama, llama2 em vez de llama2:13b)
- Feche outros programas pesados
- Verifique uso de RAM: `htop` ou `top`

## 📁 ESTRUTURA DE ARQUIVOS

```
kairo/maestro/
├── main.py                    # Ponto de entrada
├── config.py                  # Configurações
├── test_maestro.py           # Testes do sistema
├── modules/                   # Módulos cognitivos
│   ├── state_manager.py      # Memória e estado
│   ├── emotion_engine.py     # Sistema emocional
│   ├── personality_core.py   # Personalidade evolutiva
│   ├── prompt_engine.py      # Construção de prompts
│   ├── ollama_client.py      # Comunicação com Ollama
│   ├── action_executor.py    # Execução de ações
│   ├── idle_processor.py     # Processamento de ociosidade
│   └── logger.py             # Sistema de logging
├── executors/                 # "Corpos" do Kairo
│   ├── base_executor.py      # Interface base
│   └── cli_executor.py       # Interface CLI
└── data/                      # Dados persistentes (criado automaticamente)
    ├── kairo_state.json      # Estado principal
    ├── user_profiles.json    # Perfis de usuários
    └── logs/                 # Logs do sistema
```

## 🎯 PRÓXIMOS PASSOS

1. **Teste básico**: Execute e converse com o Kairo
2. **Observe evolução**: Note como a personalidade muda ao longo do tempo
3. **Experimente comandos**: Use `/status` para ver desenvolvimento
4. **Personalize**: Ajuste configurações em `config.py`

## 🆘 SUPORTE

Se encontrar problemas:

1. Execute `python test_maestro.py` para diagnóstico
2. Verifique logs em `data/logs/`
3. Consulte este arquivo de instruções
4. Verifique se Ollama está funcionando: `ollama list`

## 🎉 DIVIRTA-SE!

O Kairo é um projeto experimental de IA com personalidade evolutiva. Cada conversa é única e contribui para seu desenvolvimento. Seja paciente e observe como ele cresce!

---
**Projeto Kairo v1.0** - Sistema Maestro  
Desenvolvido com ❤️ para funcionar 100% local

