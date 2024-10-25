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

try:
    # Navega até a página
    driver.get("https://www.siam.mg.gov.br/siam/processo/index.jsp")

    # 1 - selecionar o botão para inserir um municipio
    # Localizar o link pelo href e clicar nele
    link_seloutromunic = driver.find_element(
        By.XPATH, "//a[@href='javascript:seloutromunic()']"
    )
    link_seloutromunic.click()

    # Espera um pouco para a nova janela abrir
    time.sleep(2)

    # Alterna para a nova janela #
    window_after = driver.window_handles[1]
    driver.switch_to.window(window_after)

    # html_source = driver.page_source
    # print("## CONTEUDO: ", html_source)

    ## VAI ABRIR UM NOVA TELA

    # 2 - iniserir o nome no campo de busca e clicar em buscar
    elemento = driver.find_element(By.CSS_SELECTOR, "input[name='procura_texto']")

    print(elemento.get_attribute("value"))  # Obtém o valor atual
    elemento.send_keys("UBERABA")  # Envia um texto para o campo

    link_seloutromunic = driver.find_element(
        By.XPATH, "//a[@href='javascript:pesquisar()']"
    )
    link_seloutromunic.click()

    # Encontra o link "Selecionar" pelo texto exato
    selecionar_link = driver.find_element(By.XPATH, "//a[text()='Selecionar ']")

    # Clica no link "Selecionar"
    selecionar_link.click()

    # Lida com a janela de mensagem aberta pelo javascript
    confirm = driver.switch_to.alert
    confirm.accept()

    time.sleep(3)
    driver.close()

    # Volta para a janela original (se necessário)
    driver.switch_to.window(driver.window_handles[0])

    time.sleep(1)

    link = driver.find_element(By.XPATH, "//a[@href='javascript:pesquisar()']")
    link.click()

    time.sleep(70)

    ## VAI APARECER UMA NOVA PAGINA COM UMA LISTA DE PROCESSOS
    # Encontra todos os elementos <tr> com as classes 'OraTableCellTextBand' e 'OraTableCellText'
    linhas = driver.find_elements(
        By.CSS_SELECTOR, "tr.OraTableCellTextBand, tr.OraTableCellText"
    )

    ''' 
    print(" # processando lista .........")
    lista_de_processos = []
    # OBTER OS VALORES PARA OBTER AS PAGINAS DE PROCESSOS
    for i in range(1, len(linhas)):
        # print("##############")

        colunas = linhas[i].find_elements(By.TAG_NAME, "td")
        dados = DadosProcesso()

        for coluna in colunas:
            try:
                # Tenta encontrar um elemento <a> dentro da célula
                link = coluna.find_element(By.TAG_NAME, "a")
                href = link.get_attribute("href")
                # print(f"Processo tecnico: {link.text}  *   Link encontrado: {href}")
                dados.link = href
            except NoSuchElementException:
                # Se não houver um link, imprime o texto da célula
                # print(f"Texto da coluna: {coluna.text}")
                ...

        # print(f"empreendedor: {colunas[1].text}")
        # print(f"empreendimento: {colunas[2].text}")
        # print(f"Total de processos: {colunas[3].text}")

        if (int(colunas[3].text) != 0):
            dados.empreendedor = colunas[1].text
            dados.empreendimento = colunas[2].text
            dados.total_processos = colunas[3].text

            lista_de_processos.append(dados)

        # print("##############")

        # APOS OBTER TODOS OS PROCESSOS, DEVE-SE ABRIR CADA UM DOS PROCESSOS
        print("# processando lista de dados ......")
        for data in lista_de_processos:
            print(f"data => {data.link}")

        link_seloutromunic = driver.find_element(
            By.XPATH, f"//a[@href='{lista_de_processos[0].link}']"
        )
        link_seloutromunic.click()
    '''
    e = "javascript:escolheEmprto(10129)"

    link_seloutromunic = driver.find_element(
        By.XPATH, f"//a[@href='{e}']"
    )
    link_seloutromunic.click()

    tr_elements = driver.find_elements(By.XPATH , '//table/tbody/tr')
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

    print("# buscando link ......")
    print("")
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
        # print(f"# tr: {tr.text}")
        try:
            split_text = re.split(" ", tr.text)
        except Exception as e:
            print(f">> Erro: {e}")
        if any(text in element_list for text in split_text):
            try:    
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
                    elemento_com_classe = driver.find_element(By.CLASS_NAME, 'UptInputHeader')

                    # Encontre a tabela próxima ao elemento encontrado
                    tabela = elemento_com_classe.find_element(By.XPATH, "following::table[1]")

                    # Encontre todas as linhas da tabela
                    linhas = tabela.find_elements(By.TAG_NAME, 'tr')

                    # Itere sobre cada linha
                    for linha in linhas:
                        # Encontre todas as células dentro da linha
                        celulas = linha.find_elements(By.TAG_NAME, 'td')

                        for celula in celulas:
                            try:
                                # Tente encontrar um link dentro da célula
                                link = celula.find_element(By.TAG_NAME, 'a')
                                # Pegue o href do link se ele existir
                                href = link.get_attribute('href')

                                lista_pagina_pdfs.append(href)

                            except NoSuchElementException:
                                # Se não houver link na célula, continue para a próxima célula
                                continue

                    driver.close()
                    # Volta para a janela original
                    driver.switch_to.window(driver.window_handles[0])

            except Exception as e:
                print(f"houve um erro ao obter o link: {e}")


    for link in lista_pagina_pdfs:
        print(f"link: {link}")

    ## VAI ABRIR UMA NOVA JANELA CONTENDO A LISTA DE PROCESSOS

    # 7 - nessa parte deve-se obter o link do pdf que está dentro do botão de download

    # A PARTIR DESSE PONTO SERÁ RESPONSABILIDADE DE OUTRA PARTE DO SCRIPT BAIXAR OS DADOS DO PDF E OBTER OS DADOS UTEIS DE DENTRO DELE

    # Espera a página carregar (pode ser substituído por WebDriverWait para uma abordagem mais robusta)
    time.sleep(120)

finally:
    # Fecha o navegador
    driver.quit()
