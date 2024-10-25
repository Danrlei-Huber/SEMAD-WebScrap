from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import sys

from dadosProcesso import DadosProcesso

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))


# Define o tempo máximo para carregar uma página
driver.set_page_load_timeout(90)


# Navega até a página
driver.get(
    "http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?pageheader=null&num_pt=&ano_pt=&nome_empreendedor=&cpf_cnpj_emprdor=&num_fob=&ano_fob=&cod_atividades=&cod_outros_municipios=701&nome_empreendimento=&cpf_cnpj_emp=&tipoProcesso=&num_apefoutorga=&cod_empreendimento=&ano_apefoutorga="
)

time.sleep(10)
# Encontra todos os elementos <tr> com as classes 'OraTableCellTextBand' e 'OraTableCellText'
linhas = driver.find_elements(
    By.CSS_SELECTOR, "tr.OraTableCellTextBand, tr.OraTableCellText"
)

lista_de_processos = []

for processo in lista_de_processos:
    print("abrindo processo")
    link_seloutromunic = driver.find_element(By.XPATH, f"//a[@href='{processo}']")
    link_seloutromunic.click()

    tr_elements = driver.find_elements(By.XPATH, "//table/tbody/tr")
    if not tr_elements:
        print("não há elementos")
        sys.exit()

    # Iterar sobre todos os elementos <tr> encontrados

    # AA - Autorização Ambiental
    # DLAE - Dispensa de Licenciamento Ambiental Estadual
    # LAS - Licença Ambiental Simplificada
    # LASR - Licença Ambiental Simplificada de Regularização
    # LP - Licença Previa
    # LI - Licença de Instalação
    # LO - Licença de Operação
    # LOR - Licença de Operação de Regularização

    element_list = [
        "AA",
        "DLAE",
        "LAS",
        "LASR",
        "LP",
        "LI",
        "LO",
        "LOR",
        "REVALIDACAO DE LO",
    ]

    # busca na pagina do empreendedor
    lista_pagina_pdfs = []
    for tr in tr_elements:
        print("iterando .... ")
        try:
            split_text = re.split(" ", tr.text)
        except Exception as e:
            ...
        if any(text in element_list for text in split_text):
                # Encontre o elemento <a> dentro da linha
                link = tr.find_element(By.TAG_NAME, "a")

                # Obtenha o valor do atributo href
                href = link.get_attribute("href")
                if href:
                    # abrindo a função javascript: abrindo a segunda janela
                    link.click()

                    # troca para a segunda janela
                    window_after = driver.window_handles[1]
                    driver.switch_to.window(window_after)

                    time.sleep(0.7)

                    # Localize o elemento pela classe "UptInputHeader"
                    elemento_com_classe = driver.find_element(
                        By.CLASS_NAME, "UptInputHeader"
                    )

                    # Encontre a tabela próxima ao elemento encontrado
                    tabela = elemento_com_classe.find_element(
                        By.XPATH, "following::table[1]"
                    )

                    # Encontre todas as linhas da tabela
                    linhas = tabela.find_elements(By.TAG_NAME, "tr")

                    # Itere sobre cada linha
                    for linha in linhas:
                        # Encontre todas as células dentro da linha
                        celulas = linha.find_elements(By.TAG_NAME, "td")

                        for celula in celulas:
                            try:
                                # Tente encontrar um link dentro da célula
                                link = celula.find_element(By.TAG_NAME, "a")
                                # Pegue o href do link se ele existir
                                href = link.get_attribute("href")

                                lista_pagina_pdfs.append(href)
                                print(">>> adicionado link")

                            except NoSuchElementException:
                                # Se não houver link na célula, continue para a próxima célula
                                continue

                    driver.close()
                    # Volta para a janela original
                    driver.switch_to.window(driver.window_handles[0])


