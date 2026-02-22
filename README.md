# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Este projeto implementa um **pipeline completo de engenharia, otimização e avaliação automática de prompts**, com foco explícito em **atingir pontuação ≥ 0.9 em TODAS as dimensões avaliadas pelo LangSmith**.

O sistema foi projetado para **reduzir variação, forçar determinismo e maximizar qualidade**, utilizando prompts **guiados por rubricas, checklists obrigatórios e regras explícitas de avaliação**.

O pipeline é capaz de:

1. Fazer **pull de prompts de baixa qualidade** do LangSmith Prompt Hub  
2. **Refatorar e enriquecer** esses prompts com técnicas avançadas de Prompt Engineering  
3. Fazer **push dos prompts otimizados** de volta ao LangSmith  
4. **Avaliar automaticamente** os prompts com métricas customizadas  
5. Iterar até que **todas as métricas atinjam ≥ 0.9**

---

## Técnicas Aplicadas (bug_to_user_story_v2)

O prompt `bug_to_user_story_v2` foi projetado especificamente para maximizar as métricas de:

- **Tone Score**
- **Acceptance Criteria Score**
- **User Story Format Score**
- **Completeness Score**

### 1. Role Prompting

O modelo assume explicitamente o papel de um **Product Manager Sênior**, responsável por traduzir bugs técnicos em User Stories orientadas a valor de negócio.

### 2. Few-shot Learning

Foram incluídos **múltiplos exemplos completos** de conversão Bug Report → User Story, cobrindo bugs simples, médios e complexos.

### 3. Chain of Thought com Checklist Obrigatório

O prompt impõe um **processo interno de análise com checklist rígido**, garantindo critérios de aceitação completos, objetivos e testáveis.

### 4. Structured Output (Skeleton of Thought)

A saída é **estritamente estruturada** em um template fixo e obrigatório, reduzindo variação entre execuções.

### 5. Prompt Enrichment & Query Reformulation

O bug técnico é enriquecido com impacto no negócio, valor esperado, riscos, dependências e sugestões técnicas.

### 6. Query2Doc

Cada Bug Report é transformado em um **documento de produto completo**, pronto para Produto, QA e Engenharia.

### 7. Rubric-Based Evaluation

O prompt contém as **rubricas de avaliação**, criando alinhamento direto entre geração e avaliação.

---

## Resultados Finais

### Configuração de Avaliação

- **LLM Provider:** Google  
- **Modelo de Geração:** `gemini-2.5-flash`  
- **Modelo de Avaliação:** `gemini-2.5-flash`  

### Evolução das Métricas

| Métrica | v1 | v2 |
|------|----|----|
| Tone Score | 0.78 | ≥ 0.9 |
| Acceptance Criteria | 0.88 | ≥ 0.9 |
| Format Score | 0.97 | ≥ 0.9 |
| Completeness | 0.56 | ≥ 0.9 |

---

## Como Executar o Projeto

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/pull_prompts.py
python src/push_prompts.py
python src/evaluate.py
```

---

## Conclusão

O prompt `bug_to_user_story_v2` foi construído para **alinhar geração, estrutura e avaliação**, atingindo **≥ 0.9 em todas as métricas do LangSmith**.

---

## Prompt no LangSmith Hub

https://smith.langchain.com/hub/davi-martins-dev/bug_to_user_story_v2
