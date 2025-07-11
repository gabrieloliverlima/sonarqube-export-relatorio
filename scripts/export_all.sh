#!/bin/bash

# Script para executar todos os exports do SonarQube
# Autor: Sistema de Exportação SonarQube
# Data: $(date +%Y-%m-%d)

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Função para imprimir cabeçalho
print_header() {
    echo ""
    echo "=================================="
    echo "$1"
    echo "=================================="
}

# Função para verificar se um arquivo existe
check_script() {
    local script_path=$1
    if [ ! -f "$script_path" ]; then
        print_message $RED "❌ Erro: Script $script_path não encontrado!"
        exit 1
    fi
}

# Função para executar script Python
run_python_script() {
    local script_name=$1
    local script_path="scripts/$script_name"
    
    print_header "Executando $script_name"
    
    check_script "$script_path"
    
    print_message $BLUE "🚀 Iniciando $script_name..."
    
    if python "$script_path"; then
        print_message $GREEN "✅ $script_name executado com sucesso!"
    else
        print_message $RED "❌ Erro ao executar $script_name!"
        return 1
    fi
}

# Função para criar diretório de exports se não existir
create_exports_dir() {
    if [ ! -d "exports" ]; then
        mkdir -p exports
        print_message $YELLOW "📁 Diretório exports/ criado"
    fi
}

# Função para verificar conectividade com SonarQube
check_sonarqube_connectivity() {
    print_header "Verificando Conectividade"
    
    local sonar_url=${SONAR_URL:-"http://sonarqube:9000"}
    local max_retries=30
    local retry_count=0
    
    print_message $BLUE "🔄 Verificando conectividade com SonarQube..."
    print_message $BLUE "📡 URL: $sonar_url"
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s -f -u "${SONAR_USERNAME:-admin}:${SONAR_PASSWORD:-admin}" \
           "$sonar_url/api/system/status" > /dev/null 2>&1; then
            print_message $GREEN "✅ SonarQube está disponível!"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        print_message $YELLOW "⏳ Tentativa $retry_count/$max_retries - aguardando..."
        sleep 2
    done
    
    print_message $RED "❌ SonarQube não está disponível após $max_retries tentativas"
    return 1
}

# Função para mostrar informações do ambiente
show_environment_info() {
    print_header "Informações do Ambiente"
    
    print_message $BLUE "📋 Configurações:"
    echo "   • URL SonarQube: ${SONAR_URL:-http://sonarqube:9000}"
    echo "   • Usuário: ${SONAR_USERNAME:-admin}"
    echo "   • Projeto: ${PROJECT_KEY:-teste}"              #Trocar para o PROJECT_KEY configurado na Sonar
    echo "   • Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "   • Diretório de trabalho: $(pwd)"
    echo "   • Versão Python: $(python --version 2>&1)"
}

# Função para criar relatório consolidado
create_consolidated_report() {
    print_header "Criando Relatório Consolidado"
    
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local report_file="exports/consolidated_report_${PROJECT_KEY:-teste}_${timestamp}.md"           #Trocar para o PROJECT_KEY configurado na Sonar
    
    print_message $BLUE "📄 Criando relatório consolidado..."
    
    cat > "$report_file" << EOF
# Relatório Consolidado SonarQube

**Projeto:** ${PROJECT_KEY:-teste}                                      #Trocar para o PROJECT_KEY configurado na Sonar
**Data de Exportação:** $(date '+%Y-%m-%d %H:%M:%S')
**URL SonarQube:** ${SONAR_URL:-http://sonarqube:9000}

## Arquivos Exportados

### Métricas
$(ls -la exports/metrics_* 2>/dev/null | tail -n +2 | awk '{print "- " $9 " (" $5 " bytes) - " $6 " " $7 " " $8}' || echo "- Nenhum arquivo de métricas encontrado")

### Issues
$(ls -la exports/issues_* 2>/dev/null | tail -n +2 | awk '{print "- " $9 " (" $5 " bytes) - " $6 " " $7 " " $8}' || echo "- Nenhum arquivo de issues encontrado")

### Quality Gate
$(ls -la exports/quality_gate_* 2>/dev/null | tail -n +2 | awk '{print "- " $9 " (" $5 " bytes) - " $6 " " $7 " " $8}' || echo "- Nenhum arquivo de quality gate encontrado")

## Resumo da Exportação

- **Total de arquivos:** $(ls -1 exports/ 2>/dev/null | wc -l)
- **Tamanho total:** $(du -sh exports/ 2>/dev/null | cut -f1 || echo "0")
- **Status:** Concluído com sucesso
- **Hora de conclusão:** $(date '+%Y-%m-%d %H:%M:%S')

---
*Relatório gerado automaticamente pelo sistema de exportação SonarQube*
EOF

    print_message $GREEN "✅ Relatório consolidado criado: $report_file"
}

# Função para limpar arquivos antigos (opcional)
cleanup_old_files() {
    local days_old=${1:-7}  # Padrão: 7 dias
    
    print_header "Limpeza de Arquivos Antigos"
    
    print_message $BLUE "🧹 Procurando arquivos com mais de $days_old dias..."
    
    local old_files=$(find exports/ -name "*.json" -o -name "*.xlsx" -o -name "*.csv" -o -name "*.md" | \
                     xargs ls -la 2>/dev/null | \
                     awk -v days=$days_old 'BEGIN{cmd="date -d \""days" days ago\" +%Y%m%d"; cmd | getline cutoff_date} 
                          {gsub(/-/, "", $6); if($6 < cutoff_date) print $9}' 2>/dev/null || true)
    
    if [ -n "$old_files" ]; then
        print_message $YELLOW "📋 Arquivos antigos encontrados:"
        echo "$old_files"
        
        # Comentar a linha abaixo se quiser ativar a limpeza automática
        # echo "$old_files" | xargs rm -f
        # print_message $GREEN "✅ Arquivos antigos removidos"
        
        print_message $BLUE "💡 Para remover automaticamente, descomente a linha de limpeza no script"
    else
        print_message $GREEN "✅ Nenhum arquivo antigo encontrado"
    fi
}

# Função principal
main() {
    print_header "🚀 EXPORTAÇÃO COMPLETA SONARQUBE"
    
    # Mostrar informações do ambiente
    show_environment_info
    
    # Criar diretório de exports
    create_exports_dir
    
    # Verificar conectividade
    if ! check_sonarqube_connectivity; then
        print_message $RED "❌ Não foi possível conectar ao SonarQube. Verifique se os containers estão rodando."
        exit 1
    fi
    
    # Executar scripts de exportação
    local failed_scripts=0
    
    print_header "📊 EXPORTANDO MÉTRICAS"
    if ! run_python_script "export_metrics.py"; then
        failed_scripts=$((failed_scripts + 1))
        print_message $RED "❌ Falha na exportação de métricas"
    fi
    
    print_header "🐛 EXPORTANDO ISSUES"
    if ! run_python_script "export_issues.py"; then
        failed_scripts=$((failed_scripts + 1))
        print_message $RED "❌ Falha na exportação de issues"
    fi
    
    print_header "🚪 EXPORTANDO QUALITY GATE"
    if ! run_python_script "export_quality_gate.py"; then
        failed_scripts=$((failed_scripts + 1))
        print_message $RED "❌ Falha na exportação de quality gate"
    fi
    
    # Criar relatório consolidado
    create_consolidated_report
    
    # Limpeza de arquivos antigos (opcional)
    cleanup_old_files 7
    
    # Resumo final
    print_header "📋 RESUMO FINAL"
    
    local total_files=$(ls -1 exports/ 2>/dev/null | wc -l)
    local total_size=$(du -sh exports/ 2>/dev/null | cut -f1 || echo "0")
    
    print_message $BLUE "📊 Estatísticas da exportação:"
    echo "   • Total de arquivos exportados: $total_files"
    echo "   • Tamanho total: $total_size"
    echo "   • Scripts executados: $((3 - failed_scripts))/3"
    echo "   • Falhas: $failed_scripts"
    echo "   • Diretório: exports/"
    
    if [ $failed_scripts -eq 0 ]; then
        print_message $GREEN "🎉 EXPORTAÇÃO COMPLETA REALIZADA COM SUCESSO!"
        print_message $GREEN "📁 Todos os relatórios estão disponíveis em: exports/"
    else
        print_message $YELLOW "⚠️  EXPORTAÇÃO CONCLUÍDA COM $failed_scripts FALHA(S)"
        print_message $YELLOW "📁 Relatórios parciais estão disponíveis em: exports/"
    fi
    
    # Listar arquivos exportados
    print_message $BLUE "📁 Arquivos exportados:"
    ls -la exports/ 2>/dev/null || print_message $RED "❌ Nenhum arquivo foi exportado"
    
    print_header "✅ PROCESSAMENTO CONCLUÍDO"
    
    return $failed_scripts
}

# Verificar se o script está sendo executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi