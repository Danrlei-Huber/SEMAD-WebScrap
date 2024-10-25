from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
import time
import csv


def find_processos_tecnicos(driver):
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


def processando_dados(lista_de_elementos, driver):
    lista_pagina_pdfs = []
    '''
    element_list  = [
    "AA - AUTORIZACAO AMBIENTAL",
    "DLAE - DISPENSA DE LICENCIAMENTO AMBIENTAL ESTADUAL",
    "LAS - LICENCA AMBIENTAL SIMPLIFICADA",
    "LASR - LICENCA AMBIENTAL SIMPLIFICADA DE REGULARIZACAO",
    "LP - LICENCA PREVIA", # OK
    "LI - LICENCA DE INSTALACAO", # OK
    "LO - LICENCA DE OPERACAO", # OK
    "LOR - LICENCA DE OPERACAO DE REGULARIZACAO"
    ]'''
    element_list = ["OUTORGA", "  ", " ", "", "Siam - Sistema Integrado de Informação Ambiental", "Orgão:  " ]

    for tr in lista_de_elementos:
        tds = tr.find_elements(By.TAG_NAME, "td")
        td_texts = [td.text for td in tds]
        if (len(td_texts) < 2): # aqui, tem uma comparacao para ver se a linha eh valida para acessar
            continue
        
        if td_texts[1] not in element_list:
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
                #print(f"# processando_dados - Erro ao abrir processo de regulamentação: {e}")
                continue
    return lista_pagina_pdfs


def obter_lista_de_processos_de_regularizacao(processo, driver):
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


def scrape(municipios_para_processar):
    SELENIUM_GRID_URL = f"http://localhost:4444"
    timeout = 300

    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # chrome_options.add_argument('--headless')  # Ative se não precisar da interface gráfica

    attempt = 0
    max_attempts = 3  # Máximo de tentativas de reconexão
    driver = None

    while attempt < max_attempts:
        try:
            print(f"Conectando ao Selenium Grid na URL: {SELENIUM_GRID_URL} (tentativa {attempt + 1})")
            # Cria uma conexão remota com o Selenium Grid
            remote_connection = RemoteConnection(SELENIUM_GRID_URL)
            remote_connection.set_timeout(timeout)

            # Conecte-se ao Selenium Grid com as opções definidas
            driver = webdriver.Remote(
                command_executor=remote_connection,
                options=chrome_options
            )
            driver.set_page_load_timeout(120)

            lista_pagina_pdfs = []
            link_pdfs_validos = []
            link_pdfs_nao_validos = []
            DATA_INICIO_PDFS_VALIDOS = 2020 

            for municipio in municipios_para_processar:
                print(f">> {municipio}")
                try:
                    link_municipio = f"http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?cod_outros_municipios={municipio}"
                    driver.get(link_municipio)

                    span_element = driver.find_elements(By.CSS_SELECTOR, "span.OraHeader")[1]
                    nome_municipio = span_element.text.strip()
                    num_processos = driver.find_element(By.XPATH, "//span[contains(@class, 'UptInputHeader')]").text

                    print(f"## ID: {municipio} || cidade: {nome_municipio} || num de processos: {num_processos}")

                    time.sleep(1)

                    processos_tecnicos = find_processos_tecnicos(driver)

                    for processo in processos_tecnicos:
                        lista_de_elementos = obter_lista_de_processos_de_regularizacao(processo, driver)
                        link_para_pdfs = processando_dados(lista_de_elementos, driver)
                        lista_pagina_pdfs.extend(link_para_pdfs)
                        try:
                            driver.refresh()
                            #link = driver.find_element(By.XPATH, "//a[@href='javascript:history.back()']")
                            #link.click()

                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//a[@href='javascript:history.back()']"))
                            )
                            link = driver.find_element(By.XPATH, "//a[@href='javascript:history.back()']")
                            link.click()    
                        except:
                            print("## erro ao usar .back() ....")

                            driver.refresh()
                            time.sleep(10)
                            driver.refresh()
                            print("## tentando novamente .back() ....")
                            WebDriverWait(driver, 3).until(
                                EC.presence_of_element_located((By.XPATH, "//a[@href='javascript:history.back()']"))
                            )
                            link = driver.find_element(By.XPATH, "//a[@href='javascript:history.back()']")
                            link.click()   
                            print("## processo .back() .... realizado com sucesso.") 
                except Exception as e:
                    print(f"## Erro ao processar município com ID: {municipio}: {e}")
                    continue

            # buscar os link dos PDFs
            #print("# Buscando os links dos PDFs")
            for link in lista_pagina_pdfs:
                driver.get(link)
                time.sleep(0.2)

                trs_com_links = driver.find_elements(By.XPATH, "//tr[td/a]")

                for tr in trs_com_links:
                    link = tr.find_element(By.TAG_NAME, "a")
                    href = link.get_attribute("href")
                    if href == "javascript:history.back()":
                        continue

                    parte_interna = href.split("('")[1].split("')")[0]
                    url = parte_interna.split("doc=")[1]
                    url_limpa = url.replace("%27", "").replace("(", "").replace(")", "")

                    tds = tr.find_elements(By.TAG_NAME, "td")
                    td_texts = [td.text for td in tds]

                    data = td_texts[2]
                    dia_processo, mes_processo, ano_processo = data.split("/")
                    if int(ano_processo) > DATA_INICIO_PDFS_VALIDOS:
                        link_pdfs_validos.append(url_limpa)
                    else:
                        link_pdfs_nao_validos.append(url_limpa)

            print("URLs limpas:")
            for l in link_pdfs_validos:
                print(l)
            #print("URLs (nao links válidos) limpas:")
            for l in link_pdfs_nao_validos:
                print(l)

            return link_pdfs_validos

        except WebDriverException as e:
            print(f"Erro ao conectar com o Selenium Grid: {e}")
            attempt += 1
            if attempt < max_attempts:
                print(f"Tentando reconectar... (Tentativa {attempt + 1}/{max_attempts})")
                time.sleep(5)  # Aguardar antes de tentar novamente
            else:
                print("Máximo de tentativas alcançado. Abortando operação.")
                break
        finally:
            if driver:
                print("Fechando navegador.")
                driver.quit()


def dividir_range_em_listas(x, max_num):
    intervalo = max_num // x
    listas = [list(range(i * intervalo, (i + 1) * intervalo)) for i in range(x)]
    # Incluindo o último valor que pode ter sido excluído
    listas[-1].append(max_num)
    return listas

def criar_lista(x):
    list = []
    for i in range(0, x+1):
        list.append([i])
    return list

def main():
    
    # Usar ThreadPoolExecutor para paralelizar
    with ThreadPoolExecutor(max_workers=8) as executor:
        results = executor.map(scrape, criar_lista(20))

    data = []
    for r in results:
        for i in r:
            data.append(i)

    print("============ SALVANDO EM ARQUIVO ===============")
    csv_file = 'links.txt'
    # Abrir o arquivo CSV para escrita
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Iterar pelos resultados e gravar no CSV
        for link in data:
            print(f">> {link}")
            writer.writerow([link])  # Escreve cada resultado como uma linha separada
    print("==================== FIM ========================")

if __name__ == "__main__":
    main()

