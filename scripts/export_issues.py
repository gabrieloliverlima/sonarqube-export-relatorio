#!/usr/bin/env python3
"""
Script para exportar issues (problemas) do SonarQube
"""

import os
import requests
import json
import pandas as pd
from datetime import datetime
import sys

# Configurações do SonarQube
SONAR_URL = os.getenv('SONAR_URL', 'http://sonarqube:9000')
SONAR_USERNAME = os.getenv('SONAR_USERNAME', 'admin')
SONAR_PASSWORD = os.getenv('SONAR_PASSWORD', 'admin')
PROJECT_KEY = os.getenv('PROJECT_KEY', 'teste')                 #Trocar para o PROJECT_KEY configurado na Sonar

def get_auth():
    """Retorna a autenticação para SonarQube"""
    return (SONAR_USERNAME, SONAR_PASSWORD)

def wait_for_sonarqube():
    """Aguarda o SonarQube estar disponível"""
    print("🔄 Verificando se SonarQube está disponível...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{SONAR_URL}/api/system/status", 
                                  auth=get_auth(), timeout=5)
            if response.status_code == 200:
                print("✅ SonarQube está disponível!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if i < max_retries - 1:
            print(f"⏳ Tentativa {i+1}/{max_retries} - aguardando...")
            import time
            time.sleep(2)
    
    print("❌ SonarQube não está disponível")
    return False

def get_project_issues():
    """Obtém issues do projeto"""
    print(f"🐛 Obtendo issues do projeto: {PROJECT_KEY}")
    
    url = f"{SONAR_URL}/api/issues/search"
    
    all_issues = []
    page = 1
    page_size = 500
    
    while True:
        params = {
            'componentKeys': PROJECT_KEY,
            'p': page,
            'ps': page_size,
            'facets': 'severities,types,rules,statuses'
        }
        
        try:
            response = requests.get(url, params=params, auth=get_auth())
            response.raise_for_status()
            
            data = response.json()
            issues = data.get('issues', [])
            
            if not issues:
                break
                
            all_issues.extend(issues)
            
            # Verificar se há mais páginas
            total = data.get('total', 0)
            if len(all_issues) >= total:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter issues: {e}")
            return None, None
    
    # Obter facetas (estatísticas)
    facets = data.get('facets', []) if 'data' in locals() else []
    
    print(f"📊 Total de issues encontradas: {len(all_issues)}")
    return all_issues, facets

def process_issues(issues):
    """Processa issues para exportação"""
    processed_issues = []
    
    for issue in issues:
        processed_issue = {
            'Key': issue.get('key', ''),
            'Tipo': issue.get('type', ''),
            'Severidade': issue.get('severity', ''),
            'Status': issue.get('status', ''),
            'Regra': issue.get('rule', ''),
            'Mensagem': issue.get('message', ''),
            'Componente': issue.get('component', ''),
            'Linha': issue.get('line', ''),
            'Esforço': issue.get('effort', ''),
            'Autor': issue.get('author', ''),
            'Data_Criacao': issue.get('creationDate', ''),
            'Data_Atualizacao': issue.get('updateDate', ''),
            'Tags': ','.join(issue.get('tags', [])),
            'Assignee': issue.get('assignee', ''),
            'Debt': issue.get('debt', ''),
            'Fluxo': issue.get('flows', [])
        }
        
        processed_issues.append(processed_issue)
    
    return processed_issues

def create_summary_stats(issues, facets):
    """Cria estatísticas resumidas"""
    summary = {
        'total_issues': len(issues),
        'by_type': {},
        'by_severity': {},
        'by_status': {},
        'by_rule': {}
    }
    
    # Contar por tipo
    for issue in issues:
        issue_type = issue.get('type', 'Unknown')
        summary['by_type'][issue_type] = summary['by_type'].get(issue_type, 0) + 1
    
    # Contar por severidade
    for issue in issues:
        severity = issue.get('severity', 'Unknown')
        summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
    
    # Contar por status
    for issue in issues:
        status = issue.get('status', 'Unknown')
        summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
    
    # Contar por regra (top 10)
    rule_counts = {}
    for issue in issues:
        rule = issue.get('rule', 'Unknown')
        rule_counts[rule] = rule_counts.get(rule, 0) + 1
    
    # Top 10 regras
    top_rules = sorted(rule_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    summary['by_rule'] = dict(top_rules)
    
    return summary

def export_issues_to_files(issues, facets):
    """Exporta issues para arquivos"""
    if not issues:
        print("❌ Nenhuma issue para exportar")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Processar issues
    processed_issues = process_issues(issues)
    
    # Criar estatísticas
    summary = create_summary_stats(issues, facets)
    
    # Informações do projeto
    project_info = {
        'Projeto': PROJECT_KEY,
        'Data_Exportacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'URL_SonarQube': SONAR_URL,
        'Total_Issues': len(issues)
    }
    
    # Exportar para JSON
    json_file = f"exports/issues_{PROJECT_KEY}_{timestamp}.json"
    export_data = {
        'project_info': project_info,
        'summary': summary,
        'issues': processed_issues,
        'facets': facets
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Issues exportadas para: {json_file}")
    
    # Exportar para Excel
    excel_file = f"exports/issues_{PROJECT_KEY}_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Aba com todas as issues
        df_issues = pd.DataFrame(processed_issues)
        df_issues.to_excel(writer, sheet_name='Issues', index=False)
        
        # Aba com resumo por tipo
        df_type = pd.DataFrame(list(summary['by_type'].items()), 
                              columns=['Tipo', 'Quantidade'])
        df_type.to_excel(writer, sheet_name='Resumo_Tipo', index=False)
        
        # Aba com resumo por severidade
        df_severity = pd.DataFrame(list(summary['by_severity'].items()), 
                                  columns=['Severidade', 'Quantidade'])
        df_severity.to_excel(writer, sheet_name='Resumo_Severidade', index=False)
        
        # Aba com resumo por status
        df_status = pd.DataFrame(list(summary['by_status'].items()), 
                                columns=['Status', 'Quantidade'])
        df_status.to_excel(writer, sheet_name='Resumo_Status', index=False)
        
        # Aba com top regras
        df_rules = pd.DataFrame(list(summary['by_rule'].items()), 
                               columns=['Regra', 'Quantidade'])
        df_rules.to_excel(writer, sheet_name='Top_Regras', index=False)
        
        # Aba com informações do projeto
        df_info = pd.DataFrame([project_info])
        df_info.to_excel(writer, sheet_name='Informações', index=False)
    
    print(f"✅ Issues exportadas para: {excel_file}")
    
    # Exportar para CSV
    csv_file = f"exports/issues_{PROJECT_KEY}_{timestamp}.csv"
    df_issues = pd.DataFrame(processed_issues)
    df_issues.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ Issues exportadas para: {csv_file}")

def main():
    """Função principal"""
    print("🚀 Iniciando exportação de issues do SonarQube")
    print(f"📋 Projeto: {PROJECT_KEY}")
    print(f"🔗 URL: {SONAR_URL}")
    
    # Verificar se SonarQube está disponível
    if not wait_for_sonarqube():
        sys.exit(1)
    
    # Obter issues
    issues, facets = get_project_issues()
    
    if issues is not None:
        # Exportar para arquivos
        export_issues_to_files(issues, facets)
        print("\n🎉 Exportação de issues concluída com sucesso!")
    else:
        print("❌ Falha na exportação de issues")
        sys.exit(1)

if __name__ == "__main__":
    main()