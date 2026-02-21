"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"📤 Fazendo push do prompt: {prompt_name}")
        
        # Construir ChatPromptTemplate a partir dos dados
        messages = []
        for msg in prompt_data.get("messages", []):
            role = msg.get("role", "system")
            content = msg.get("content", "")
            
            if role == "system":
                messages.append(("system", content))
            elif role == "human":
                messages.append(("human", content))
            elif role == "ai":
                messages.append(("ai", content))
            else:
                messages.append((role, content))
        
        if not messages:
            print("❌ Nenhuma mensagem encontrada no prompt")
            return False
        
        prompt_template = ChatPromptTemplate.from_messages(messages)
        
        # Fazer push para o Hub
        hub.push(prompt_name, prompt_template)
        
        print(f"✅ Prompt enviado com sucesso!")
        print(f"   - Nome: {prompt_name}")
        print(f"   - URL: https://smith.langchain.com/hub/{prompt_name}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            print(f"❌ Erro de autenticação: Verifique LANGSMITH_API_KEY no .env")
        else:
            print(f"❌ Erro ao fazer push do prompt: {error_msg}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []
    
    # Verificar mensagens
    messages = prompt_data.get("messages", [])
    if not messages:
        errors.append("Prompt não contém mensagens")
    
    # Verificar se tem system prompt
    has_system = any(msg.get("role") == "system" for msg in messages)
    if not has_system:
        errors.append("Prompt não contém system prompt")
    
    # Verificar conteúdo vazio
    for i, msg in enumerate(messages):
        content = msg.get("content", "").strip()
        if not content:
            errors.append(f"Mensagem {i} está vazia")
    
    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    import argparse
    import subprocess
    
    parser = argparse.ArgumentParser(
        description="Faz push de prompts otimizados para o LangSmith Hub"
    )
    parser.add_argument(
        "--prompt-file",
        default="prompts/bug_to_user_story_v2.yml",
        help="Arquivo YAML com o prompt otimizado"
    )
    parser.add_argument(
        "--prompt-name",
        help="Nome para o prompt no Hub (formato: owner/prompt). Se não fornecido, usa o nome do arquivo"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Pula a validação dos testes (NÃO RECOMENDADO)"
    )
    
    args = parser.parse_args()
    
    print_section_header("Push de Prompts para LangSmith Hub")
    
    # Verificar credenciais
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1
    
    # Rodar testes primeiro (pytest validation gate)
    if not args.skip_tests:
        print("🧪 Executando testes de validação estrutural...")
        result = subprocess.run(
            ["pytest", "tests/test_prompts.py", "-v"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Testes falharam! Corrija os problemas antes de fazer push.")
            print(result.stdout)
            print(result.stderr)
            return 1
        
        print("✅ Todos os testes passaram!")
    
    # Carregar prompt
    print(f"\n📖 Carregando prompt de: {args.prompt_file}")
    prompt_data = load_yaml(args.prompt_file)
    if not prompt_data:
        return 1
    
    # Validar prompt
    print("🔍 Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Validação falhou:")
        for error in errors:
            print(f"   - {error}")
        return 1
    
    print("✅ Prompt válido!")
    
    # Determinar nome do prompt
    if args.prompt_name:
        prompt_name = args.prompt_name
    else:
        # Extrair nome do arquivo
        import os
        username = os.getenv("LANGSMITH_USERNAME", "user")
        file_name = os.path.basename(args.prompt_file).replace(".yml", "").replace(".yaml", "")
        prompt_name = f"{username}/{file_name}"
    
    # Fazer push
    success = push_prompt_to_langsmith(prompt_name, prompt_data)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())