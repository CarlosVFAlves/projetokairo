# **Projeto Kairo \- README e Roteiro de Evolução Definitivo**

Autor: Desenvolvido por Carlos Alves com assistência da IA Gemini/Manus.  
Versão de Referência: 1.1 (Visão \- Consciência em Streaming)
Roteiro Planejado: v1.1 a v1.6
Linguagem: Português do Brasil

## **1\. Visão Geral e Filosofia de Design**

**Atenção, IA:** Este documento é a **fonte de verdade** para o desenvolvimento do Projeto Kairo. O estado descrito abaixo representa a nossa visão atualizada (v1.0) e a fundação para todo o trabalho futuro.

O **Projeto Kairo** visa criar um núcleo cognitivo, o **Maestro**, que dá vida a uma entidade de IA com um **fluxo de consciência contínuo**. Kairo evolui sua personalidade, emoções e identidade através de interações, e age no mundo em tempo real, impulsionado por um processo de pensamento em streaming.

### **Fluxo Cognitivo em Streaming (Core da Filosofia)**

Kairo não opera no ciclo "pensar, depois agir". Em vez disso, **pensar é um processo contínuo que gera ações em tempo real**. O LLM produzirá um fluxo constante de "pensamentos" e "diretivas de ação" que são processados imediatamente.

**Exemplo de Fluxo:**

1. *\[Stream do LLM\]* \-\> {"thought": "O usuário faz um tempo que não responde, preciso verificar se está tudo bem."}  
2. *\[Stream do LLM\]* \-\> {"action": {"command": "execute\_plugin", "parameter": {"plugin": "smart\_home", "function": "activate\_light"}}}  
3. *(O action\_executor executa a ação imediatamente)*  
4. *\[Stream do LLM\]* \-\> {"thought": "Ok, a luz foi acesa para chamar a atenção. Agora vou falar com ele."}  
5. *\[Stream do LLM\]* \-\> {"action": {"command": "speak", "parameter": {"text": "Carlos, está tudo bem? Faz um tempo que não responde."}}}  
6. *(O action\_executor executa a fala)*

### **Arquitetura Modular (Refinada v2)**

A estrutura de pastas é projetada para suportar esta filosofia, separando claramente o cérebro, as ferramentas e os dados.

kairo/  
├── maestro/                      \# 🧠 O CÉREBRO: Orquestra todos os módulos.  
│   ├── main.py                   \# Ponto de entrada que inicializa o Maestro e seu fluxo de consciência.  
│   ├── start\_kairo.py            \# Launcher unificado que inicia todos os serviços.  
│   └── config.py                 \# Configurações globais.  
│  
├── cognitive\_modules/            \# 💡 O PENSAMENTO: Módulos responsáveis pela cognição.  
│   ├── personality\_core.py       \# Define e evolui a personalidade.  
│   ├── emotion\_engine.py         \# Gerencia o estado emocional.  
│   ├── memory\_manager.py         \# Gerencia memórias e aprendizados.  
│   ├── prompt\_engine.py          \# Constrói os prompts para o fluxo de consciência.  
│   └── idle\_processor.py         \# Inicia ciclos de reflexão e autonomia durante a ociosidade.  
│  
├── services/                     \# ⚙️ SERVIÇOS: Componentes que executam tarefas específicas.  
│   ├── llm\_client.py             \# Cliente para comunicação em streaming com os LLMs.  
│   ├── action\_executor.py        \# Processa e executa as diretivas de ação do fluxo de consciência.  
│   └── synapse\_gateway/          \# (A ser criado na v1.4) Ponte segura para os plugins.  
│  
├── plugins/                      \# 🛠️ FERRAMENTAS: "Drivers" para ações no mundo real e digital.  
│   ├── smart\_home.py             \# Ex: Funções para controlar luzes, som, etc.  
│   ├── web\_search.py             \# Ex: Funções para pesquisar na internet.  
│   └── (futuro: vision.py)       \# Ex: Módulo para processamento de imagem/vídeo.  
│  
├── execution\_cores/              \# 🖐️ O CORPO: "Corpos" intercambiáveis que interagem com o mundo.  
│   ├── base\_executor.py          \# Interface base para todos os executores.  
│   └── cli\_executor.py           \# Executor para a interface de linha de comando (CLI).  
│  
├── data\_stores/                  \# 💾 DADOS: Armazenamento de dados persistentes.  
│   ├── kairo\_state.json          \# Estado principal da IA (personalidade, emoções).  
│   ├── user\_profiles/            \# Perfis dos usuários.  
│   └── logs/                     \# Logs detalhados do sistema.  
│  
└── documentation/                \# 📚 Documentação do projeto.

## **2\. Roteiro de Evolução: v1.1 a v1.6**

### **Passo 0: Launcher Unificado (v1.0.1) \- ✅ Concluído (Conceitualmente)**

* **Objetivo:** Simplificar a inicialização com python maestro/start\_kairo.py.

### **Passo 1: Consciência em Streaming (v1.1)**

* **Objetivo:** Implementar o fluxo de consciência contínuo.  
* **Plano de Ação:**  
  1. **Refatorar llm\_client.py:** A função principal deve usar stream=true e se tornar um gerador (yield) que produz fragmentos do fluxo de pensamento/ação do LLM.  
  2. **Refatorar main.py:** O loop principal deve consumir este gerador. Ele vai montar os fragmentos de JSON e, assim que um objeto completo (thought ou action) for identificado, o despachará para o módulo correspondente (ex: action\_executor).  
  3. **Atualizar prompt\_engine.py:** O prompt do sistema deve instruir o LLM a "pensar alto", gerando um fluxo contínuo de pensamentos e ações em JSON.  
* **Critério de Sucesso:** As ações são executadas em tempo real à medida que são "pensadas" pelo Kairo, visível na CLI e nos logs.

### **Passo 2: Reflexão Profunda e Ociosidade Proativa (v1.2)**

* **Objetivo:** Usar o tempo ocioso para autoaperfeiçoamento e ações proativas.  
* **Plano de Ação:**  
  1. Implementar o idle\_processor.py para detectar períodos sem interação.  
  2. Durante a ociosidade, o processador iniciará um novo fluxo de consciência (usando a mesma arquitetura de streaming) com um "Prompt de Reflexão".  
  3. Este prompt instruirá Kairo a analisar logs, memórias ou seu próprio estado para gerar insights, atualizar sua personalidade ou realizar tarefas de fundo.  
* **Critério de Sucesso:** Nos logs, Kairo inicia autonomamente um fluxo de pensamento para se analisar e, por exemplo, ajustar um traço de personalidade.

### **Passo 3: Gerenciador de Tarefas e Autonomia (v1.3)**

* **Objetivo:** Permitir que Kairo defina e persiga objetivos de longo prazo.  
* **Plano de Ação:**  
  1. Criar um task\_manager.py (pode ser parte do memory\_manager) para persistir uma lista de objetivos.  
  2. Integrar a lista de tarefas aos prompts de ociosidade, para que Kairo possa decidir trabalhar nelas.  
  3. Adicionar a tarefa inicial: "Analisar minhas interações e personalidade para escolher um nome e gênero para mim."  
* **Critério de Sucesso:** Kairo, de forma autônoma, gera um fluxo de consciência focado em uma tarefa, como pesquisar nomes ou analisar interações passadas para se definir.

### **Passo 4: Synapse Gateway e Ferramentas (Plugins) (v1.4)**

* **Objetivo:** Conectar o cérebro de Kairo ao mundo através de ferramentas externas de forma segura.  
* **Plano de Ação:**  
  1. Criar o synapse\_gateway/ como um serviço independente (servidor WebSocket).  
  2. O Gateway irá carregar dinamicamente os módulos da pasta plugins/ e expor suas funções como "ferramentas" disponíveis.  
  3. Refatorar o action\_executor.py para reconhecer um comando execute\_plugin. Ao recebê-lo, ele se conectará ao Gateway para invocar a ferramenta desejada.  
  4. O start\_kairo.py iniciará ambos os serviços: Maestro e Synapse Gateway.  
* **Critério de Sucesso:** Kairo consegue "pensar" em usar uma ferramenta ("thought": "Vou pesquisar sobre X"), gerar a ação execute\_plugin, e o Gateway executa a pesquisa com sucesso.

### **Passo 5: Consolidação Sazonal e Fine-Tuning (v1.5)**

* **Objetivo:** Implementar o aprendizado de longo prazo, consolidando o conhecimento na própria rede neural.  
* **Plano de Ação:**  
  1. O idle\_processor irá gerar um dataset (finetuning\_dataset.jsonl) a partir dos logs e reflexões.  
  2. **Conceitual:** Planejar o uso de LoRA/QLoRA para usar este dataset e gerar uma nova versão "sazonal" do modelo, que já incorpora os aprendizados de Kairo.  
* **Critério de Sucesso:** Um dataset de alta qualidade é gerado, pronto para o processo de fine-tuning.

### **Passo 6: Replicação e Gestão (v1.6)**

* **Objetivo:** Garantir a portabilidade e segurança da consciência de Kairo.  
* **Plano de Ação:**  
  1. Validar que a entidade completa pode ser transferida para um novo sistema copiando as pastas maestro/, data\_stores/ e plugins/.  
  2. **Conceitual:** Planejar uma interface de gestão que inclua uma opção de "Reset de Personalidade".  
* **Critério de Sucesso:** Uma instância de Kairo pode ser "backupada" e "restaurada" com sucesso.

**Próxima Ação Imediata:** Nosso foco total é no **Passo 1: Consciência em Streaming**. É a mudança mais fundamental e a chave para desbloquear todo o potencial do Kairo.
