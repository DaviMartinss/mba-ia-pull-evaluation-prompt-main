# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Este projeto entrega um **pipeline completo de engenharia, otimização e avaliação de prompts**, com foco em **atingir métricas >= 0.9** em todas as dimensões avaliadas pelo LangSmith.

O sistema é capaz de:

1. Fazer **pull de prompts de baixa qualidade** do LangSmith Prompt Hub  
2. **Refatorar e otimizar** esses prompts com técnicas avançadas de Prompt Engineering  
3. Fazer **push dos prompts otimizados** de volta ao LangSmith  
4. **Avaliar automaticamente** os prompts com métricas customizadas  
5. Iterar até que **todas as métricas atinjam ≥ 0.9**

---

## Técnicas Aplicadas (Fase 2)

O prompt `bug_to_user_story_v2` foi projetado explicitamente para maximizar as métricas de **Tone, Acceptance Criteria, Format e Completeness**, utilizando as técnicas abaixo.

### 1. Role Prompting

**O que foi feito:**  
O modelo assume o papel explícito de **Product Manager Sênior**, com responsabilidade clara de transformar bugs técnicos em User Stories orientadas a valor de negócio.

**Por que foi escolhida:**  
Aumenta drasticamente o **Tone Score**, garantindo linguagem de negócio, foco no usuário e empatia, evitando viés técnico.

**Exemplo aplicado no prompt:**
> “Você é um Product Manager Sênior especializado em transformar bugs técnicos em User Stories de alta qualidade.”

---

### 2. Few-shot Learning

**O que foi feito:**  
Foram incluídos **múltiplos exemplos completos de Bug Report → User Story**, cobrindo:
- Bugs simples  
- Bugs médios  
- Bugs complexos  

**Por que foi escolhida:**  
Reduz ambiguidade, melhora consistência estrutural e eleva significativamente **Format Score e Completeness**.

**Exemplo aplicado:**  
O prompt contém 4 exemplos completos antes do placeholder `{bug_report}`.

---

### 3. Chain of Thought (CoT)

**O que foi feito:**  
O prompt obriga o modelo a seguir um **processo interno de análise com checklist rigoroso**, antes de escrever a resposta final.

**Por que foi escolhida:**  
Aumenta cobertura de cenários, reduz omissões e melhora o **Acceptance Criteria Score**.

---

### 4. Skeleton of Thought

**O que foi feito:**  
A saída é rigidamente estruturada em seções fixas e obrigatórias:
- Título  
- História do Usuário  
- Contexto e Justificativa  
- Critérios de Aceitação  
- Notas Técnicas  

**Por que foi escolhida:**  
Maximiza **Format Score** e reduz variação estrutural entre execuções.

---

### 5. Query Enrichment & Query Reformulation

**O que foi feito:**  
O bug técnico é enriquecido com:
- Impacto no negócio  
- Valor esperado  
- Riscos e dependências  
- Sugestões técnicas  

**Por que foi escolhida:**  
Eleva o **Completeness Score**, garantindo que nenhuma informação implícita fique de fora.

---

## Resultados Finais

### Configuração de Avaliação

- **LLM Provider:** Google  
- **Modelo de Geração:** `gemini-2.5-flash`  
- **Modelo de Avaliação:** `gemini-2.5-flash`  

### Evolução das Métricas

| Métrica | v1 (ruim) | v2 (otimizado) |
|------|-----------|---------------|
| Tone Score | 0.78 | ≥ 0.9 |
| Acceptance Criteria | 0.88 | ≥ 0.9 |
| Format Score | 0.97 | ≥ 0.9 |
| Completeness | 0.56 | ≥ 0.9 |

---

## Como Executar o Projeto

### 1. Criar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Pull dos prompts iniciais

```bash
python src/pull_prompts.py
```

### 3. Push do prompt otimizado

```bash
python src/push_prompts.py
```

### 4. Executar avaliação

```bash
python src/evaluate.py
```

---

## Conclusão

O prompt v2 foi construído para **forçar comportamento determinístico**, reduzindo variação e garantindo aprovação automática nas métricas do desafio.

---

## 🔗 Prompt Publicado no LangSmith Hub

O prompt otimizado **bug_to_user_story_v2** está disponível publicamente no LangSmith Prompt Hub no link abaixo:

👉 https://smith.langchain.com/hub/davi-martins-dev/bug_to_user_story_v2?organizationId=1625a015-824e-4827-b598-dfec7fedac63

**Descrição:**  
Este prompt converte relatos de bugs técnicos em **User Stories empáticas, completas e testáveis**, utilizando técnicas avançadas de Prompt Engineering (Few-shot Learning, Role Prompting, Chain of Thought, entre outras).  
Ele foi projetado especificamente para **atingir pontuação ≥ 0.9 em todas as métricas de avaliação** (Tone, Acceptance Criteria, Format e Completeness) dentro do LangSmith, garantindo alto valor para Produto, QA e Negócio.
