import re
import requests
from io import BytesIO
from PyPDF2 import PdfReader
from collections import defaultdict

# Função para buscar e organizar palavras no PDF usando PyPDF2
def buscar_palavras_no_pdf(url, palavras, palavra_prioritaria):
    try:
        # Tenta fazer o download do PDF
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Verifica se houve erro no download
    except requests.exceptions.RequestException as e:
        print(f"Erro ao baixar o PDF do link {url}: {e}")
        return None, None, {}

    try:
        # Tenta ler o conteúdo do PDF usando PyPDF2
        pdf_file = BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)
        texto_completo = ""
        palavras_encontradas = defaultdict(list)  # Dicionário para organizar o conteúdo

        # Tenta extrair o texto de cada página do PDF
        for page_num in range(len(pdf_reader.pages)):
            pagina = pdf_reader.pages[page_num]
            texto_pagina = pagina.extract_text()
            texto_completo += texto_pagina

            # Verifica se o texto foi extraído corretamente
            if texto_pagina:
                # Busca a palavra prioritária "resíduos" primeiro
                for match in re.finditer(rf'\b{palavra_prioritaria}\b', texto_pagina, re.IGNORECASE):
                    # Captura o contexto após a palavra
                    contexto_pos_match = texto_pagina[match.end():match.end()+400].strip()  
                    palavras_encontradas[palavra_prioritaria].append({
                        'pagina': page_num + 1,
                        'conteudo': texto_pagina.strip(),
                        'contexto': contexto_pos_match  # Adiciona o contexto
                    })

                # Depois busca as outras palavras
                for palavra in palavras:
                    if palavra != palavra_prioritaria:  # Evita buscar novamente pela palavra prioritária
                        for match in re.finditer(rf'\b{palavra}\b', texto_pagina, re.IGNORECASE):
                            # Captura o contexto após a palavra
                            contexto_pos_match = texto_pagina[match.end():match.end()+200].strip()  
                            palavras_encontradas[palavra].append({
                                'pagina': page_num + 1,
                                'conteudo': texto_pagina.strip(),
                                'contexto': contexto_pos_match  # Adiciona o contexto
                            })

        # Caso o texto esteja vazio
        if not texto_completo.strip():
            print(f"Não foi possível extrair texto do PDF no link {url}.")
            return None, None, {}

    except Exception as e:
        print(f"Erro ao processar o PDF do link {url}: {e}")
        return None, None, {}

    # Verifica se "resíduos" foi encontrado e se as outras palavras foram encontradas
    link_com_residuos = bool(palavras_encontradas.get(palavra_prioritaria))
    link_com_outras_palavras = any(
        palavra in palavras_encontradas for palavra in palavras if palavra != palavra_prioritaria
    )

    return link_com_residuos, link_com_outras_palavras, palavras_encontradas

# Função para ler links de um arquivo de texto
def ler_links_do_arquivo(caminho_arquivo):
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            links = [linha.strip() for linha in arquivo.readlines() if linha.strip()]
        return links
    except FileNotFoundError:
        print(f"Arquivo {caminho_arquivo} não encontrado.")
        return []

# Função para gravar dados em um arquivo
def salvar_em_arquivo(caminho_arquivo, conteudo):
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
    except Exception as e:
        print(f"Erro ao escrever no arquivo {caminho_arquivo}: {e}")

palavras_a_procurar = ["DMR", "MTR", "resíduos", "Ibama", "IBAMA", "ibama"] # AQUI MUDA
palavra_prioritaria = "resíduos"

# Lê os links do arquivo
arquivo_links = "links.txt"  # Substitua pelo caminho correto do seu arquivo
links = ler_links_do_arquivo(arquivo_links)

# Listas para armazenar os resultados
links_com_residuos = []
links_com_outras_palavras = []
dados_encontrados = ""

# Processa cada link
for link in links:
    print(f"\nProcessando link: {link}")
    encontrou_residuos, encontrou_outras, palavras_encontradas = buscar_palavras_no_pdf(link, palavras_a_procurar, palavra_prioritaria)

    # Armazena o link conforme as palavras encontradas
    if encontrou_residuos:
        links_com_residuos.append(link)
    if encontrou_outras:
        links_com_outras_palavras.append(link)

    # Montar os dados encontrados para salvar em arquivo
    if palavras_encontradas:
        dados_encontrados += f"\nLink: {link}\n"
        for palavra, detalhes in palavras_encontradas.items():
            dados_encontrados += f"\nPalavra-chave: '{palavra}'\n"
            for detalhe in detalhes:
                dados_encontrados += f"Página {detalhe['pagina']}:\n"
                dados_encontrados += detalhe['conteudo'][:500] + "\n"
                dados_encontrados += f"Contexto pós-match: {detalhe['contexto']}\n"  # Exibe o contexto adicional
                dados_encontrados += "-" * 80 + "\n"

# Salva os dados encontrados no arquivo out1.txt
salvar_em_arquivo("out/dados-encontrados.txt", dados_encontrados)

# Salva os links com a palavra "resíduos" no arquivo out2.txt
salvar_em_arquivo("out/links-com-residuos.txt", "\n".join(links_com_residuos))

# Exibe os links com as palavras encontradas
print("\nLinks contendo a palavra 'resíduos':")
for link in links_com_residuos:
    print(link)

print("\nLinks contendo outras palavras (DMR, MTR):")
for link in links_com_outras_palavras:
    print(link)
