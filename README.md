# Python Selenium Project

Este é um projeto de automação de navegador utilizando Selenium com Python. O projeto utiliza um ambiente virtual `venv` para gerenciar as dependências.

## Requisitos

- Python 3.11.0
- Java 11
- Pip (gerenciador de pacotes do Python)
- Navegador compatível (Chrome)

## Configuração do Ambiente

### 1. Clonar o Repositório

Clone o repositório para sua máquina local:

```bash
git clone git@github.com:PGA-Brazil/SEMAD-WebScrap.git
cd SEMAD-WebScrap
```

### 2. Criar e Ativar o Ambiente Virtual
```bash
# windows
python -m venv venv
.\venv\Scripts\activate
```

```bash
# linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Iniciar o selenium grid
```bash
java -jar selenium-server-4.24.0.jar standalone 
```

## Execução do Projeto
Para executar o script principal, use:
```bash
python main.py
```