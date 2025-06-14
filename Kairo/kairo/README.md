# Projeto Kairo - Sistema Maestro

## Visão Geral

O Projeto Kairo é uma IA local com personalidade evolutiva, baseada no sistema Spectro anterior, mas com a capacidade de desenvolver sua própria personalidade através das interações.

## Diferenças do Spectro

- **Spectro**: Personalidade fixa e definida (sarcástica, traços pré-definidos)
- **Kairo**: Personalidade evolutiva que se desenvolve através das interações

## Estrutura do Projeto

```
kairo/
├── maestro/                    # Sistema principal (cérebro)
│   ├── main.py                # Ponto de entrada
│   ├── config.py              # Configurações globais
│   ├── modules/               # Módulos cognitivos
│   │   ├── logger.py          # Sistema de logging
│   │   ├── state_manager.py   # Gerenciamento de estado/memória
│   │   ├── emotion_engine.py  # Sistema emocional
│   │   ├── personality_core.py # Núcleo de personalidade evolutiva
│   │   ├── prompt_engine.py   # Construção de prompts
│   │   ├── ollama_client.py   # Cliente para modelos locais
│   │   ├── action_executor.py # Execução de ações
│   │   └── idle_processor.py  # Processamento de ociosidade
│   ├── executors/             # "Corpos" intercambiáveis
│   │   ├── base_executor.py   # Interface base
│   │   └── cli_executor.py    # Executor para linha de comando
│   └── data/                  # Dados persistentes
│       ├── kairo_state.json   # Estado principal
│       ├── profiles/          # Perfis de usuários
│       └── logs/              # Logs do sistema
├── manager/                   # Software de gerenciamento
│   ├── app.py                 # Interface web Flask
│   ├── static/                # CSS, JS, imagens
│   ├── templates/             # Templates HTML
│   └── api/                   # APIs de gerenciamento
└── docs/                      # Documentação
```

## Status Atual

### ✅ Concluído
- Estrutura de pastas completa
- Sistema de configuração com personalidade evolutiva
- Sistema de logging especializado
- Ponto de entrada principal (main.py)

### 🔄 Em Desenvolvimento
- Módulos cognitivos (state_manager, emotion_engine, etc.)
- Executor CLI
- Interface de gerenciamento

### ⏳ Planejado
- Integração com Ollama
- Testes e documentação
- Empacotamento final

## Características Principais

### Sistema de Personalidade Evolutiva
- Kairo começa com traços neutros (5.0/10)
- Desenvolve personalidade através das interações
- 8 traços principais: curiosity, empathy, creativity, logic, humor, assertiveness, patience, openness
- Taxa de aprendizado configurável

### Sistema Emocional
- 6 emoções: joy, sadness, anger, fear, surprise, interest
- Decaimento natural ao longo do tempo
- Influência nas respostas e comportamento

### Sistema de Logging Avançado
- Logs específicos para mudanças de personalidade
- Acompanhamento de eventos de aprendizado
- Logs de decisões e interações
- Facilita análise da evolução do Kairo

## Tecnologias

- **Python 3.8+**: Linguagem principal
- **Ollama**: Modelos de IA locais
- **Flask**: Interface web de gerenciamento
- **JSON**: Persistência de dados
- **Threading**: Processamento assíncrono

## Próximos Passos

1. Implementar módulos cognitivos
2. Criar executor CLI para testes
3. Desenvolver interface de gerenciamento
4. Integrar com Ollama
5. Testes e documentação

## Autor

Desenvolvido por Carlos Alves com assistência da Manus AI.

