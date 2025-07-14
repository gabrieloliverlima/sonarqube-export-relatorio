# 🚀 SonarQube Docker Compose com Exportação de Relatórios

Este projeto fornece uma solução completa para executar o SonarQube via Docker Compose com scripts automatizados para exportação de relatórios de análise de código.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Configuração](#-instalação-e-configuração)
- [Como Usar](#-como-usar)
- [Scripts de Exportação](#-scripts-de-exportação)
- [Formatos de Relatório](#-formatos-de-relatório)
- [Troubleshooting](#-troubleshooting)
- [Configurações Avançadas](#-configurações-avançadas)
- [Exemplos Práticos](#-exemplos-práticos)
- [Manutenção](#-manutenção)

## 🎯 Visão Geral

Este projeto oferece:

- **SonarQube Community** rodando em Docker
- **PostgreSQL** como banco de dados
- **Scripts Python** para exportação automática de relatórios
- **Múltiplos formatos** de saída (JSON, Excel, CSV)
- **Relatórios consolidados** com estatísticas
- **Sistema de backup** para os exports

### 🔧 Componentes

- **SonarQube LTS Community**: Análise estática de código
- **PostgreSQL 15**: Banco de dados robusto
- **Python 3.11**: Scripts de exportação
- **Scripts Bash**: Automação e utilitários

## 📁 Estrutura do Projeto

```
/
├── docker-compose.yml              # Configuração dos containers
├── sonar-project.properties        # Configurações do projeto
├── scripts/                        # Scripts de exportação
│   ├── export_metrics.py           # Exporta métricas do código
│   ├── export_issues.py            # Exporta issues/problemas
│   ├── export_quality_gate.py      # Exporta Quality Gate
│   └── export_all.sh               # Executa todos os exports
├── exports/                        # Relatórios gerados
├── src/                           # Código fonte do projeto
└── README.md                       # Este arquivo
```

## 🛠️ Pré-requisitos

### Software Necessário

- **Docker** (v20.10+)
- **Docker Compose** (v2.0+)
- **SonarScanner** (para análise de código)
- **Git** (para controle de versão)

### Recursos do Sistema

- **RAM**: Mínimo 4GB, recomendado 8GB
- **Disco**: Mínimo 10GB livres
- **CPU**: 2 cores recomendados

### Portas Utilizadas

- **9000**: SonarQube Web Interface
- **9092**: SonarQube Search
- **5432**: PostgreSQL (interno)

## 🚀 Instalação e Configuração

### 1. Clonar/Preparar o Projeto

```bash
# Clonar a Repo

```

### 2. Configurar Credenciais

#### Opção A: Usar Token (Recomendado)

1. **Editar `docker-compose.yml`**:
   ```yaml
   environment:
     - SONAR_URL=http://sonarqube:9000
     - SONAR_TOKEN=seu_token_aqui
     - PROJECT_KEY=teste
   ```

#### Opção B: Usar Usuário/Senha

1. **Editar `docker-compose.yml`**:
   ```yaml
   environment:
     - SONAR_URL=http://sonarqube:9000
     - SONAR_USERNAME=admin
     - SONAR_PASSWORD=sua_senha_aqui
     - PROJECT_KEY=teste
   ```

### 3. Iniciar os Serviços

```bash
# Subir todos os containers
docker-compose up -d

# Verificar status
docker-compose ps

# Acompanhar logs do SonarQube
docker-compose logs -f sonarqube
```

### 4. Configurar SonarQube

1. **Acessar**: http://localhost:9000
2. **Login inicial**: admin/admin
3. **Alterar senha** quando solicitado
4. **Gerar token**: My Account → Security → Generate Tokens

### 5. Analisar o Código

```bash
# Opção 1: SonarScanner local
sonar-scanner \
  -Dsonar.projectKey=teste \
  -Dsonar.sources=Main \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.token=seu_token_aqui

# Opção 2: SonarScanner via Docker
docker run --rm   -e SONAR_HOST_URL="http://192.168.100.10:9000" \
-e SONAR_TOKEN=xxxxxxxxxxxxxxxxx   -v "$(pwd):/usr/src"   \
sonarsource/sonar-scanner-cli
```

## 📊 Como Usar

### Comandos Principais

```bash
# Executar todos os exports (RECOMENDADO)
docker-compose exec sonar-exporter bash scripts/export_all.sh

# Exportar apenas métricas
docker-compose exec sonar-exporter python scripts/export_metrics.py

# Exportar apenas issues
docker-compose exec sonar-exporter python scripts/export_issues.py

# Exportar apenas Quality Gate
docker-compose exec sonar-exporter python scripts/export_quality_gate.py


```

### Comandos de Diagnóstico

```bash
# Ver logs do exportador
docker-compose logs sonar-exporter

# Ver logs do SonarQube
docker-compose logs sonarqube

# Entrar no container
docker-compose exec sonar-exporter bash


```

## 📋 Scripts de Exportação

### 1. `export_metrics.py`
**Exporta métricas do projeto:**
- Linhas de código (ncloc)
- Complexidade e complexidade cognitiva
- Cobertura de testes
- Bugs, vulnerabilidades, code smells
- Ratings de qualidade (A-E)
- Dívida técnica
- Status do Quality Gate

### 2. `export_issues.py`
**Exporta issues detalhadas:**
- Lista completa de problemas
- Classificação por tipo/severidade
- Estatísticas por status
- Top 10 regras mais violadas
- Informações de localização no código

### 3. `export_quality_gate.py`
**Exporta Quality Gate:**
- Status atual (PASSED/FAILED)
- Condições e seus resultados
- Histórico de análises
- Configurações do Quality Gate

### 4. `export_all.sh`
**Executa todos os exports:**
- Verifica conectividade
- Executa todos os scripts
- Gera relatório consolidado
- Limpa arquivos antigos
- Estatísticas finais

## 📄 Formatos de Relatório

### Arquivos Gerados

```
exports/
├── metrics_Maximus_20240101_120000.json      # Métricas completas
├── metrics_Maximus_20240101_120000.xlsx      # Métricas Excel
├── metrics_Maximus_20240101_120000.csv       # Métricas CSV
├── issues_Maximus_20240101_120000.json       # Issues completas
├── issues_Maximus_20240101_120000.xlsx       # Issues Excel (múltiplas abas)
├── issues_Maximus_20240101_120000.csv        # Issues CSV
├── quality_gate_Maximus_20240101_120000.json # Quality Gate completo
├── quality_gate_Maximus_20240101_120000.xlsx # Quality Gate Excel
├── quality_gate_conditions_Maximus_20240101_120000.csv # Condições CSV
└── consolidated_report_Maximus_20240101_120000.md # Relatório consolidado
```

### Formatos Suportados

- **JSON**: Dados estruturados completos
- **Excel**: Múltiplas abas organizadas
- **CSV**: Dados tabulares para análise
- **Markdown**: Relatórios legíveis



## 🔧 Troubleshooting

### Problemas Comuns

#### 1. Erro 401 (Unauthorized)
```bash
# Verificar credenciais
docker-compose exec sonar-exporter python scripts/test_credentials.py

# Soluções:
# - Verificar token no docker-compose.yml
# - Gerar novo token no SonarQube
# - Verificar usuário/senha
```

#### 2. Erro 404 (Project Not Found)
```bash
# Verificar se projeto existe
docker-compose exec sonar-exporter python scripts/check_project.py

# Soluções:
# - Executar sonar-scanner para analisar código
# - Criar projeto manualmente no SonarQube
# - Verificar PROJECT_KEY no docker-compose.yml
```

#### 3. SonarQube Não Inicia
```bash
# Verificar logs
docker-compose logs sonarqube

# Soluções comuns:
# - Aumentar memória Docker
# - Verificar portas em uso
# - Aguardar inicialização completa (pode levar 2-3 minutos)
```

#### 4. Sem Permissão nos Scripts
```bash
# Dar permissão
chmod +x scripts/*.sh

# Ou executar diretamente
docker-compose exec sonar-exporter bash scripts/export_all.sh
```

### Comandos de Debug

```bash
# Verificar containers
docker-compose ps

# Verificar logs
docker-compose logs --tail=50 sonarqube
docker-compose logs --tail=50 sonar-exporter

# Verificar conectividade
docker-compose exec sonar-exporter curl http://sonarqube:9000/api/system/status

# Verificar variáveis
docker-compose exec sonar-exporter env | grep SONAR

# Reiniciar serviços
docker-compose restart
```

## ⚙️ Configurações Avançadas

### Personalizar Métricas

**Editar `export_metrics.py`**:
```python
# Adicionar/remover métricas na lista
metrics = [
    'ncloc',
    'complexity',
    'suas_metricas_customizadas'
]
```

### Configurar Limpeza Automática

**Editar `export_all.sh`**:
```bash
# Alterar dias para limpeza
cleanup_old_files 30  # 30 dias ao invés de 7
```

### Adicionar Novos Projetos

**Editar `docker-compose.yml`**:
```yaml
# Adicionar mais containers exportadores
sonar-exporter-projeto2:
  # configurações...
  environment:
    - PROJECT_KEY=Projeto2
```

### Configurar Recursos

**Editar `docker-compose.yml`**:
```yaml
sonarqube:
  # Limitar recursos
  deploy:
    resources:
      limits:
        memory: 4G
        cpus: '2'
```

### Práticas Recomendadas

1. **Use tokens** ao invés de usuário/senha
2. **Configure firewall** para limitar acesso à porta 9000
3. **Faça backup regular** do banco de dados
4. **Monitore logs** para acessos suspeitos
5. **Mantenha containers atualizados**


🚀 **Happy Coding!**