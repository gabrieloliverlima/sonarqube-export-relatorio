#!/usr/bin/env python3
"""
Script para exportar Quality Gate do SonarQube
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
PROJECT_KEY = os.getenv('PROJECT_KEY', 'teste')                         #Trocar para o PROJECT_KEY configurado na Sonar

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

def get_project_quality_gate():
    """Obtém status do Quality Gate do projeto"""
    print(f"🚪 Obtendo Quality Gate do projeto: {PROJECT_KEY}")
    
    url = f"{SONAR_URL}/api/qualitygates/project_status"
    params = {
        'projectKey': PROJECT_KEY
    }
    
    try:
        response = requests.get(url, params=params, auth=get_auth())
        response.raise_for_status()
        
        data = response.json()
        return data.get('projectStatus', {})
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao obter Quality Gate: {e}")
        return None

def get_quality_gate_details():
    """Obtém detalhes do Quality Gate"""
    print("🔍 Obtendo detalhes do Quality Gate...")
    
    # Primeiro, obter o Quality Gate associado ao projeto
    url = f"{SONAR_URL}/api/qualitygates/get_by_project"
    params = {
        'project': PROJECT_KEY
    }
    
    try:
        response = requests.get(url, params=params, auth=get_auth())
        response.raise_for_status()
        
        qg_data = response.json()
        qg_id = qg_data.get('qualityGate', {}).get('id')
        
        if not qg_id:
            print("⚠️  Nenhum Quality Gate específico encontrado, usando padrão")
            return {}
        
        # Obter detalhes do Quality Gate
        details_url = f"{SONAR_URL}/api/qualitygates/show"
        details_params = {
            'id': qg_id
        }
        
        details_response = requests.get(details_url, params=details_params, auth=get_auth())
        details_response.raise_for_status()
        
        return details_response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Erro ao obter detalhes do Quality Gate: {e}")
        return {}

def get_project_analysis_history():
    """Obtém histórico de análises do projeto"""
    print("📈 Obtendo histórico de análises...")
    
    url = f"{SONAR_URL}/api/project_analyses/search"
    params = {
        'project': PROJECT_KEY,
        'ps': 50  # Últimas 50 análises
    }
    
    try:
        response = requests.get(url, params=params, auth=get_auth())
        response.raise_for_status()
        
        data = response.json()
        return data.get('analyses', [])
        
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Erro ao obter histórico: {e}")
        return []

def process_quality_gate_data(qg_status, qg_details, analyses):
    """Processa dados do Quality Gate"""
    
    # Status atual
    current_status = {
        'Status': qg_status.get('status', 'UNKNOWN'),
        'Projeto': PROJECT_KEY,
        'Data_Analise': qg_status.get('analysisDate', ''),
        'Ignorar_Warnings': qg_status.get('ignoredConditions', False)
    }
    
    # Condições do Quality Gate
    conditions = []
    for condition in qg_status.get('conditions', []):
        conditions.append({
            'Metrica': condition.get('metricKey', ''),
            'Comparador': condition.get('comparator', ''),
            'Valor_Limite': condition.get('threshold', ''),
            'Valor_Atual': condition.get('actualValue', ''),
            'Status': condition.get('status', ''),
            'Erro_Mensagem': condition.get('errorMessage', '')
        })
    
    # Detalhes do Quality Gate
    qg_info = {
        'ID': qg_details.get('id', ''),
        'Nome': qg_details.get('name', ''),
        'Default': qg_details.get('isDefault', False),
        'Total_Conditions': len(qg_details.get('conditions', []))
    }
    
    # Histórico de análises
    analysis_history = []
    for analysis in analyses:
        analysis_history.append({
            'Data': analysis.get('date', ''),
            'Versao': analysis.get('projectVersion', ''),
            'Revision': analysis.get('revision', ''),
            'Eventos': ','.join([e.get('name', '') for e in analysis.get('events', [])])
        })
    
    return current_status, conditions, qg_info, analysis_history

def export_quality_gate_to_files(qg_status, qg_details, analyses):
    """Exporta Quality Gate para arquivos"""
    if not qg_status:
        print("❌ Nenhum dado de Quality Gate para exportar")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Processar dados
    current_status, conditions, qg_info, analysis_history = process_quality_gate_data(
        qg_status, qg_details, analyses
    )
    
    # Informações do projeto
    project_info = {
        'Projeto': PROJECT_KEY,
        'Data_Exportacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'URL_SonarQube': SONAR_URL,
        'Status_Quality_Gate': current_status['Status']
    }
    
    # Exportar para JSON
    json_file = f"exports/quality_gate_{PROJECT_KEY}_{timestamp}.json"
    export_data = {
        'project_info': project_info,
        'current_status': current_status,
        'conditions': conditions,
        'quality_gate_info': qg_info,
        'analysis_history': analysis_history
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Quality Gate exportado para: {json_file}")
    
    # Exportar para Excel
    excel_file = f"exports/quality_gate_{PROJECT_KEY}_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        # Aba com status atual
        df_status = pd.DataFrame([current_status])
        df_status.to_excel(writer, sheet_name='Status_Atual', index=False)
        
        # Aba com condições
        if conditions:
            df_conditions = pd.DataFrame(conditions)
            df_conditions.to_excel(writer, sheet_name='Condicoes', index=False)
        
        # Aba com informações do Quality Gate
        df_qg_info = pd.DataFrame([qg_info])
        df_qg_info.to_excel(writer, sheet_name='Quality_Gate_Info', index=False)
        
        # Aba com histórico de análises
        if analysis_history:
            df_history = pd.DataFrame(analysis_history)
            df_history.to_excel(writer, sheet_name='Historico_Analises', index=False)
        
        # Aba com informações do projeto
        df_info = pd.DataFrame([project_info])
        df_info.to_excel(writer, sheet_name='Informações', index=False)
    
    print(f"✅ Quality Gate exportado para: {excel_file}")
    
    # Exportar condições para CSV
    if conditions:
        csv_file = f"exports/quality_gate_conditions_{PROJECT_KEY}_{timestamp}.csv"
        df_conditions = pd.DataFrame(conditions)
        df_conditions.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ Condições do Quality Gate exportadas para: {csv_file}")

def print_quality_gate_summary(qg_status, qg_details):
    """Imprime resumo do Quality Gate"""
    print("\n" + "="*50)
    print("📊 RESUMO DO QUALITY GATE")
    print("="*50)
    
    status = qg_status.get('status', 'UNKNOWN')
    status_emoji = "✅" if status == "OK" else "❌" if status == "ERROR" else "⚠️"
    
    print(f"{status_emoji} Status: {status}")
    print(f"📋 Projeto: {PROJECT_KEY}")
    print(f"📅 Data da análise: {qg_status.get('analysisDate', 'N/A')}")
    
    conditions = qg_status.get('conditions', [])
    if conditions:
        print(f"\n📋 Condições ({len(conditions)}):")
        for i, condition in enumerate(conditions, 1):
            cond_status = condition.get('status', 'UNKNOWN')
            cond_emoji = "✅" if cond_status == "OK" else "❌" if cond_status == "ERROR" else "⚠️"
            metric = condition.get('metricKey', '')
            actual = condition.get('actualValue', '')
            threshold = condition.get('threshold', '')
            comparator = condition.get('comparator', '')
            
            print(f"  {i}. {cond_emoji} {metric}: {actual} {comparator} {threshold}")
    
    qg_name = qg_details.get('name', 'N/A')
    print(f"\n🚪 Quality Gate: {qg_name}")
    print("="*50)

def main():
    """Função principal"""
    print("🚀 Iniciando exportação de Quality Gate do SonarQube")
    print(f"📋 Projeto: {PROJECT_KEY}")
    print(f"🔗 URL: {SONAR_URL}")
    
    # Verificar se SonarQube está disponível
    if not wait_for_sonarqube():
        sys.exit(1)
    
    # Obter dados do Quality Gate
    qg_status = get_project_quality_gate()
    qg_details = get_quality_gate_details()
    analyses = get_project_analysis_history()
    
    if qg_status:
        # Mostrar resumo
        print_quality_gate_summary(qg_status, qg_details)
        
        # Exportar para arquivos
        export_quality_gate_to_files(qg_status, qg_details, analyses)
        print("\n🎉 Exportação de Quality Gate concluída com sucesso!")
    else:
        print("❌ Falha na exportação de Quality Gate")
        sys.exit(1)

if __name__ == "__main__":
    main()