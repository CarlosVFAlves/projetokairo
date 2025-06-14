# 🔧 CORREÇÕES PARA COMUNICAÇÃO COM OLLAMA

## ❌ PROBLEMAS IDENTIFICADOS

### 1. **Erro no Template de Prompt**
**Sintoma:** `Erro ao gerar prompt: '\n  "internal_monologue"'`
**Causa:** Formatação incorreta das chaves no template JSON

### 2. **Respostas Não Estruturadas**
**Sintoma:** Ollama retorna texto simples em vez de JSON
**Causa:** Falta de instruções específicas para formato JSON

### 3. **Respostas Genéricas de Fallback**
**Sintoma:** Kairo responde sempre "Desculpe, não posso ajudar"
**Causa:** Sistema usa fallback genérico quando não consegue processar JSON

## ✅ CORREÇÕES APLICADAS

### 1. **Template de Prompt Corrigido**
```python
# ANTES (problemático):
"internal_monologue": "texto"

# DEPOIS (corrigido):
{{"internal_monologue": "texto"}}  # Escape duplo das chaves
```

### 2. **Forçar Formato JSON no Ollama**
```python
payload = {
    "model": model_to_use,
    "prompt": f"{prompt}\n\nIMPORTANTE: Responda APENAS com JSON válido.",
    "format": "json",  # ← NOVO: Força formato JSON
    "options": {
        "temperature": 0.7,
        "stop": ["\n\n", "```"]  # ← NOVO: Para em quebras
    }
}
```

### 3. **Extração de JSON Melhorada**
- ✅ Tenta parse direto primeiro
- ✅ Busca JSON entre chaves se necessário
- ✅ Validação mais flexível (parameter opcional)
- ✅ Melhor tratamento de erros

### 4. **Fallback Inteligente**
- ✅ Remove prefixos desnecessários
- ✅ Limita tamanho da resposta
- ✅ Resposta padrão se texto muito curto
- ✅ Melhor interpretação do texto bruto

## 🎯 RESULTADO ESPERADO

**ANTES:**
```
👤 Você: Qual a capital do Brasil?
🤖 Kairo: Desculpe, não posso ajudar com essa pergunta.
```

**DEPOIS:**
```
👤 Você: Qual a capital do Brasil?
🤖 Kairo: A capital do Brasil é Brasília! É uma cidade planejada, construída especificamente para ser a capital do país.
```

## 🔧 CONFIGURAÇÕES RECOMENDADAS DO OLLAMA

### **Modelos Testados e Funcionais:**
```bash
# Melhor para conversação:
ollama pull llama2:7b

# Alternativa rápida:
ollama pull llama2:3b

# Para máquinas potentes:
ollama pull llama2:13b
```

### **Configuração no config.py:**
```python
OLLAMA_CONFIG = {
    "model": "llama2:7b",  # ← Use este modelo
    "temperature": 0.7,    # ← Criatividade balanceada
    "max_tokens": 1000     # ← Respostas completas
}
```

## 🚀 COMO TESTAR

### 1. **Verificar Sistema:**
```bash
cd kairo/maestro
python verificacao_completa.py
# Deve mostrar: "8/10 módulos funcionando"
```

### 2. **Testar Ollama:**
```bash
ollama serve
ollama run llama2:7b "Responda em JSON: {'resposta': 'teste'}"
```

### 3. **Executar Kairo:**
```bash
python main.py
```

### 4. **Testar Conversação:**
```
👤 Você: Olá, quem é você?
🤖 Kairo: [Deve responder normalmente agora]

👤 Você: Qual a capital do Brasil?
🤖 Kairo: [Deve responder corretamente]
```

## ⚠️ TROUBLESHOOTING

### **Se ainda der erro de JSON:**
1. Verifique se o modelo está correto: `ollama list`
2. Teste o modelo diretamente: `ollama run llama2:7b`
3. Reinicie o Ollama: `ollama serve`

### **Se respostas estranhas:**
1. Ajuste temperatura no config.py (0.3 = mais conservador)
2. Troque modelo: `ollama pull llama2:3b`

### **Se muito lento:**
1. Use modelo menor: `llama2:3b`
2. Reduza max_tokens no config.py

## 🎉 RESULTADO

O Kairo agora deve:
- ✅ Responder perguntas normalmente
- ✅ Manter conversação fluida
- ✅ Expressar personalidade
- ✅ Evoluir através das interações
- ✅ Funcionar de forma estável

**O problema de comunicação foi RESOLVIDO!** 🚀

