# Vamos criar o script para extrair informações de um arquivo TXT e salvar o resultado em out.txt.

import re

def extract_residue_info(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        text = file.read()
        
    residue_data = []
    
    # Dividir o texto em seções (ex: páginas)
    pages = text.split("Página")  # Ajuste conforme necessário para o seu arquivo

    for page in pages:
        info = {
            "Número do MTR": re.search(r'MTR nº (\d+)', page),
            "Data de Emissão": re.search(r'data da emissão:\s*(\d{2}/\d{2}/\d{4})', page),
            "Identificação do Gerador": re.search(r'Identificação do Gerador\s*:\s*([^\n]+)', page),
            "Identificação do Destinador": re.search(r'Identificação do Destinador\s*:\s*([^\n]+)', page),
            "Município": re.search(r'Município:\s*([^\n]+)', page),
            "Estado": re.search(r'Estado:\s*([^\n]+)', page),
            "CPF/CNPJ": re.search(r'CPF/CNPJ:\s*([^\n]+)', page),
            "Razão Social": re.search(r'Razão Social:\s*([^\n]+)', page),
            "Mais Informações": re.search(r'mais informações:\s*([^\n]+)', page, re.IGNORECASE),
            "Tipo de Resíduo": re.search(r'Tipo de resíduo:\s*([^\n]+)', page)
        }

        # Limpar e organizar os dados
        for key in info.keys():
            if info[key]:
                info[key] = info[key].group(1).strip()
            else:
                info[key] = None
        
        residue_data.append(info)

    return residue_data

# Criando um arquivo de texto para exemplo
input_txt_path = 'out/dados-encontrados.txt'  # Local onde está o arquivo TXT
output_txt_path = 'out.txt'  # Caminho do arquivo de saída

# Executando a função para extrair dados
residue_info = extract_residue_info(input_txt_path)

# Salvando os resultados em out.txt
with open(output_txt_path, 'w', encoding='utf-8') as out_file:
    for index, info in enumerate(residue_info):
        out_file.write(f"Página {index + 1}:\n")
        for key, value in info.items():
            out_file.write(f"{key}: {value}\n")
        out_file.write("\n" + "-" * 30 + "\n")

output_txt_path
