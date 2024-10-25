from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# CONFIGURAÇÕES DO SELENIUM
# Define o tempo máximo para carregar uma página
driver.set_page_load_timeout(120)

# Números que nao possuem municipios associados
excluir_numeros = [766, 722, 715, 702, 595, 535, 468, 389, 263]

# Lista de números a serem processados, excluindo os indesejados
municipios_para_processar = [
    number for number in range(1, 854) if number not in excluir_numeros
]

def find_processos_tecnicos():
    processos = []
    try:
        colunas = driver.find_elements(By.XPATH, "//tr[td/a]")

        for coluna in colunas:
            try:
                link = coluna.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                aux = coluna.find_elements(By.TAG_NAME, "td")

                try:
                    qatd_processos = int(aux[3].text)
                    if qatd_processos >= 2:
                        processos.append(href)
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

    for tr in lista_de_elementos:
        tds = tr.find_elements(By.TAG_NAME, "td")
        td_texts = [td.text for td in tds]
        if (len(td_texts) < 2): # aqui, tem uma comparacao para ver se a linha eh valida para acessar
            continue

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
        time.sleep(1.2) # tempo necessario para carregar a tabela de processos
        elementos_trs = driver.find_elements(By.XPATH, "//table/tbody/tr")
        return elementos_trs
    except Exception as e:
        print(f"# elementos_trs: {elementos_trs}")
        print(f"# obter_lista_de_processos_de_regularizacao - Erro ao abrir link: {e}")


def main():
    try:
        # Navega até a página
        municipios_para_processar = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
        lista_pagina_pdfs = []
        link_pdfs_validos = []
        link_pdfs_nao_validos = []
        DATA_INICIO_PDFS_VALIDOS = 2020 

        for municipio in municipios_para_processar:
            try:
                #print(f"## processando municipio com ID: {municipio}")
                link_municipio = f"http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?pageheader=null&num_pt=&ano_pt=&nome_empreendedor=&cpf_cnpj_emprdor=&num_fob=&ano_fob=&cod_atividades=&cod_outros_municipios={municipio}&nome_empreendimento=&cpf_cnpj_emp=&tipoProcesso=&num_apefoutorga=&cod_empreendimento=&ano_apefoutorga="
                driver.get(link_municipio)

                span_element = driver.find_elements(By.CSS_SELECTOR, "span.OraHeader")[1]
                nome_municipio = span_element.text.strip()
                num_processos = driver.find_element(By.XPATH, "//span[contains(@class, 'UptInputHeader')]").text

                print(f"## ID: {municipio} || cidade: {nome_municipio} || num de processos: {num_processos}")

                time.sleep(1)

                #print("## processando todos os registros de empreendedores do municipio")
                processos_tecnicos = find_processos_tecnicos()

                for processo in processos_tecnicos:
                    #print("## processando lista de regulamentação do empreendedor")
                    lista_de_elementos = obter_lista_de_processos_de_regularizacao(processo)
                    #print("## obtendo a lista de links para a pagina de pdfs")
                    link_para_pdfs = processando_dados(lista_de_elementos)
                    lista_pagina_pdfs.extend(link_para_pdfs) 

                    driver.refresh()
                    link = driver.find_element(By.XPATH, "//a[@href='javascript:history.back()']")
                    link.click()

            except Exception as e:
                print(f"## erro ao obter os dados do municipio com ID: {municipio}\n{e}")
                continue

        
        # buscar os link dos PDFs
        print("# buscando os link dos PDFs")
        for link in lista_pagina_pdfs:
            driver.get(link)
            time.sleep(0.2)

            trs_com_links = driver.find_elements(By.XPATH, "//tr[td/a]")

            for tr in trs_com_links:
                link = tr.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                if (href == "javascript:history.back()"):
                    continue

                parte_interna = href.split("('")[1].split("')")[0]
                url = parte_interna.split("doc=")[1]
                url_limpa = url.replace("%27", "").replace("(", "").replace(")", "")

                tds = tr.find_elements(By.TAG_NAME, "td")
                td_texts = [td.text for td in tds]
                
                data = td_texts[2]
                dia_processo, mes_processo, ano_processo = data.split("/")
                if (int(ano_processo) > DATA_INICIO_PDFS_VALIDOS):
                    link_pdfs_validos.append(url_limpa)
                else: 
                    link_pdfs_nao_validos.append(url_limpa)

        print("urls (links validos) limpas")
        for l in link_pdfs_validos:
            print(l)
        print("urls (links nao validos) limpas")
        for l in link_pdfs_nao_validos:
            print(l)  

    except Exception as e:
        print(f"ocorreu um erro: {e}")
    finally:
        print("fechando navegador")
        driver.quit()



if __name__ == "__main__":
    main()



