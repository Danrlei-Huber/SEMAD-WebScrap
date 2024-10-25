from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import re

from dadosProcesso import DadosProcesso

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# CONFIGURAÇÕES DO SELENIUM
# Define o tempo máximo para carregar uma página
driver.set_page_load_timeout(120)

# Números que nao possuem municipios associados
excluir_numeros = [766, 722, 715, 702, 595, 535, 468, 389, 263]

class Dat:
    def __init__(self, proceso, len):
        self.proceso = proceso
        self.len = len

# Lista de números a serem processados, excluindo os indesejados
municipios_para_processar = [
    number for number in range(1, 854) if number not in excluir_numeros
]


def find_processos_tecnicos():
    processos = []

    # Encontra todos os elementos <tr> com as classes 'OraTableCellTextBand' e 'OraTableCellText'
    linhas = driver.find_elements(
        By.CSS_SELECTOR, "tr.OraTableCellTextBand, tr.OraTableCellText"
    )

    # OBTER OS VALORES PARA OBTER AS PAGINAS DE PROCESSOS
    for i in range(1, len(linhas)):
        try:
            colunas = linhas[i].find_elements(By.TAG_NAME, "td")
            dados = DadosProcesso()

            for coluna in colunas:
                try:
                    link = coluna.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute("href")
                    dados.link = href
                except NoSuchElementException:
                    # Se não houver um link, imprime o texto da célula
                    # print(f"Texto da coluna: {coluna.text}")
                    ...

            if (int(colunas[3].text) != 0):
                dados.empreendedor = colunas[1].text
                dados.empreendimento = colunas[2].text
                dados.total_processos = colunas[3].text

                processos.append(dados.link)

        except Exception as e:
            print(f"# find_processos_tecnicos - houve um erro: {e}")
    return processos

def find_processos_tecnicos2():
    processos = []
    try:
        colunas = driver.find_elements(By.XPATH, "//tr[td/a]")

        for coluna in colunas:
            try:
                link = coluna.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                aux = coluna.find_elements(By.TAG_NAME, "td")

                try:
                    numero_int = int(aux[3].text)
                    if numero_int != 0:
                        processos.append(Dat(href, numero_int))
                except ValueError:
                    continue
            except NoSuchElementException:
                continue
    except Exception as e:
        print(f"# find_processos_tecnicos - houve um erro: {e}")
 
    return processos

def obter_paginas_dos_pdfs(linhas):
    lista_pagina_pdfs = []
    for linha in linhas:
        # Encontre todas as células dentro da linha
        celulas = linha.find_elements(By.TAG_NAME, "td")

        for celula in celulas:
            try:
                link = celula.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")

                lista_pagina_pdfs.append(href)
            except NoSuchElementException:
                continue
    return lista_pagina_pdfs


def processando_dados(lista_de_elementos):
    lista_pagina_pdfs = []

    # AA - Autorização Ambiental
    # DLAE - Dispensa de Licenciamento Ambiental Estadual
    # LAS - Licença Ambiental Simplificada
    # LASR - Licença Ambiental Simplificada de Regularização
    # LP - Licença Previa
    # LI - Licença de Instalação
    # LO - Licença de Operação
    # LOR - Licença de Operação de Regularização

    element_list  = [
    "AA - AUTORIZACAO AMBIENTAL",
    "DLAE - DISPENSA DE LICENCIAMENTO AMBIENTAL ESTADUAL",
    "LAS - LICENCA AMBIENTAL SIMPLIFICADA",
    "LASR - LICENCA AMBIENTAL SIMPLIFICADA DE REGULARIZACAO",
    "LP - LICENCA PREVIA",
    "LI - LICENCA DE INSTALACAO",
    "LO - LICENCA DE OPERACAO",
    "LOR - LICENCA DE OPERACAO DE REGULARIZACAO"
    ]
    print("## procesando trs ##")
    print(f"## lista de elementos: {lista_de_elementos}")
    for tr in lista_de_elementos:
        tds = tr.find_elements(By.TAG_NAME, "td")
        td_texts = [td.text for td in tds]
        if (len(td_texts) < 2):
            continue
        print(f"::: {td_texts}")
        if td_texts[1] in element_list:
            try:
                link = tr.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")

                link.click()

                # troca para a segunda janela
                window_after = driver.window_handles[1]
                driver.switch_to.window(window_after)

                time.sleep(0.2)

                # Localize o elemento pela classe "UptInputHeader"
                elemento_com_classe = driver.find_element(By.CLASS_NAME, "UptInputHeader")
                # Encontre a tabela próxima ao elemento encontrado
                tabela = elemento_com_classe.find_element(By.XPATH, "following::table[1]")
                # Encontre todas as linhas da tabela
                linhas = tabela.find_elements(By.TAG_NAME, "tr")

                lista_pagina_pdfs = obter_paginas_dos_pdfs(linhas)
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                print(f"# processando_dados - Erro ao abrir processo de regulamentação: {e}")
    
    return lista_pagina_pdfs


def obter_lista_de_processos_de_regularizacao(processo):
    elementos_trs = []
    try:
        link_seloutromunic = driver.find_element(By.XPATH, f"//a[@href='{processo}']")
        link_seloutromunic.click()
        time.sleep(1.2)
        elementos_trs = driver.find_elements(By.XPATH, "//table/tbody/tr")
        return elementos_trs
    except Exception as e:
        print(f"# elementos_trs: {elementos_trs}")
        print(f"# obter_lista_de_processos_de_regularizacao - Erro ao abrir link: {e}")


def main():
    try:
        municipios_para_processar = [2,3,4,5]
        lista_pagina_pdfs = []

        for municipio in municipios_para_processar:
            try:
                print(f"## processando municipio com ID: {municipio}")
                link_municipio = f"http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?pageheader=null&num_pt=&ano_pt=&nome_empreendedor=&cpf_cnpj_emprdor=&num_fob=&ano_fob=&cod_atividades=&cod_outros_municipios={municipio}&nome_empreendimento=&cpf_cnpj_emp=&tipoProcesso=&num_apefoutorga=&cod_empreendimento=&ano_apefoutorga="
                driver.get(link_municipio)

                time.sleep(1)

                print("## processando todos os registros de empreendedores do municipio")
                processos_tecnicos = find_processos_tecnicos2()
                #processos_tecnicos = ["javascript:escolheEmprto(528356)", "javascript:escolheEmprto(545203)"]

                for processo in processos_tecnicos:
                    data_processo = processo.proceso
                    data_len = processo.len
                    
                    lista_de_elementos = obter_lista_de_processos_de_regularizacao(data_processo)

                    print(f"processo: {data_processo} --- len: {data_len}")
                    link_para_pdfs = processando_dados(lista_de_elementos)
                    if link_para_pdfs:
                        lista_pagina_pdfs.extend(lista_pagina_pdfs) 

                    driver.refresh()
                    link = driver.find_element(By.XPATH, "//a[@href='javascript:history.back()']")
                    link.click()

            except Exception as e:
                print(f"## erro ao obter os dados do municipio com ID: {municipio}\n{e}")
                continue

    finally:
        print("fechando navegador")
        driver.quit()



if __name__ == "__main__":
    main()
