import re
import requests
from io import BytesIO
from PyPDF2 import PdfReader

# Função para buscar o conteúdo completo das páginas que contêm palavras-chave
def buscar_conteudo_paginas_chave(url, palavras):
    try:
        # Tenta fazer o download do PDF
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Verifica se houve erro no download
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o PDF do link {url}: {e}")
        return

    try:
        # Tenta ler o conteúdo do PDF usando PyPDF2
        pdf_file = BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)
        paginas_com_chaves = ""

        # Tenta extrair o texto de cada página do PDF
        for page_num in range(len(pdf_reader.pages)):
            pagina = pdf_reader.pages[page_num]
            texto_pagina = pagina.extract_text()

            # Verifica se o texto foi extraído corretamente
            if texto_pagina:
                for palavra in palavras:
                    if re.search(rf'\b{palavra}\b', texto_pagina, re.IGNORECASE):
                        paginas_com_chaves += f"\n\nPágina {page_num + 1} (contém '{palavra}'):\n"
                        paginas_com_chaves += texto_pagina
                        break  # Para de buscar outras palavras na mesma página se uma for encontrada

        # Caso o texto esteja vazio ou nenhuma palavra-chave seja encontrada
        if not paginas_com_chaves.strip():
            print(f"Nenhuma palavra-chave encontrada no PDF no link {url}.")
            return

        return paginas_com_chaves

    except Exception as e:
        print(f"Erro ao processar o PDF do link {url}: {e}")
        return

# Função para ler links de um arquivo de texto
def ler_links_do_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r') as arquivo:
            links = [linha.strip() for linha in arquivo.readlines() if linha.strip()]
        return links
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return []

# Lista de palavras a buscar
palavras_a_procurar = ["DMR", "MTR", "resíduos"]

# Lê os links do arquivo
arquivo_links = "links.txt"  # Substitua pelo caminho correto do seu arquivo
links = ler_links_do_arquivo(arquivo_links)

# Processa cada link
for link in links:
    print(f"\nProcessando link: {link}")
    conteudo_paginas = buscar_conteudo_paginas_chave(link, palavras_a_procurar)
    if conteudo_paginas:
        print(conteudo_paginas)  # Exibe o conteúdo das páginas que contêm as palavras-chave
