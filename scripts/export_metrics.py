#!/usr/bin/env python3
"""
Script para exportar métricas do SonarQube
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
PROJECT_KEY = os.getenv('PROJECT_KEY', 'teste')                                 #Trocar para o PROJECT_KEY configurado na Sonar

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

def get_project_metrics():
    """Obtém métricas do projeto"""
    print(f"📊 Obtendo métricas do projeto: {PROJECT_KEY}")
    
    # Métricas principais
    metrics = [
        'ncloc',                    # Linhas de código
        'complexity',               # Complexidade
        'cognitive_complexity',     # Complexidade cognitiva
        'duplicated_lines_density', # Densidade de duplicação
        'coverage',                 # Cobertura de testes
        'bugs',                     # Bugs
        'vulnerabilities',          # Vulnerabilidades
        'security_hotspots',        # Hotspots de segurança
        'code_smells',              # Code smells
        'sqale_rating',             # Maintainability rating
        'reliability_rating',       # Reliability rating
        'security_rating',          # Security rating
        'sqale_index',              # Technical debt
        'alert_status'              # Quality gate status
    ]
    
    url = f"{SONAR_URL}/api/measures/component"
    params = {
        'component': PROJECT_KEY,
        'metricKeys': ','.join(metrics)
    }
    
    try:
        response = requests.get(url, params=params, auth=get_auth())
        response.raise_for_status()
        
        data = response.json()
        if 'component' not in data:
            print("❌ Projeto não encontrado no SonarQube")
            return None
            
        return data['component']['measures']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao obter métricas: {e}")
        return None

def export_metrics_to_files(metrics_data):
    """Exporta métricas para arquivos"""
    if not metrics_data:
        print("❌ Nenhuma métrica para exportar")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Processar dados
    processed_data = []
    for measure in metrics_data:
        metric_name = measure['metric']
        value = measure.get('value', 'N/A')
        
        # Converter ratings para texto
        rating_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D', '5': 'E'}
        if metric_name.endswith('_rating') and value in rating_map:
            display_value = f"{rating_map[value]} ({value})"
        else:
            display_value = value
            
        processed_data.append({
            'Métrica': metric_name,
            'Valor': display_value,
            'Valor_Raw': value
        })
    
    # Criar DataFrame
    df = pd.DataFrame(processed_data)
    
    # Adicionar informações do projeto
    project_info = {
        'Projeto': PROJECT_KEY,
        'Data_Exportacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'URL_SonarQube': SONAR_URL
    }
    
    # Exportar para JSON
    json_file = f"exports/metrics_{PROJECT_KEY}_{timestamp}.json"
    export_data = {
        'project_info': project_info,
        'metrics': processed_data
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Métricas exportadas para: {json_file}")
    
    # Exportar para Excel
    excel_file = f"exports/metrics_{PROJECT_KEY}_{timestamp}.xlsx"
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Métricas', index=False)
        
        # Adicionar informações do projeto
        info_df = pd.DataFrame([project_info])
        info_df.to_excel(writer, sheet_name='Informações', index=False)
    
    print(f"✅ Métricas exportadas para: {excel_file}")
    
    # Exportar para CSV
    csv_file = f"exports/metrics_{PROJECT_KEY}_{timestamp}.csv"
    df.to_csv(csv_file, index=False, encoding='utf-8')
    print(f"✅ Métricas exportadas para: {csv_file}")

def main():
    """Função principal"""
    print("🚀 Iniciando exportação de métricas do SonarQube")
    print(f"📋 Projeto: {PROJECT_KEY}")
    print(f"🔗 URL: {SONAR_URL}")
    
    # Verificar se SonarQube está disponível
    if not wait_for_sonarqube():
        sys.exit(1)
    
    # Obter métricas
    metrics = get_project_metrics()
    
    if metrics:
        # Exportar para arquivos
        export_metrics_to_files(metrics)
        print("\n🎉 Exportação de métricas concluída com sucesso!")
    else:
        print("❌ Falha na exportação de métricas")
        sys.exit(1)

if __name__ == "__main__":
    main()