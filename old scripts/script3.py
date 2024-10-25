from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
import time
import re
import sys

from dadosProcesso import DadosProcesso

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# Define o tempo máximo para carregar uma página
driver.set_page_load_timeout(90)

# Números que nao possuem municipios associados
excluir_numeros = [702, 35]

# Lista de números a serem processados, excluindo os indesejados
municipios_para_processar = [
    number for number in range(1, 854) if number not in excluir_numeros
]

# Marca o tempo de início
start_time = time.time()

try:
    lista_links_validos = []
    for number in municipios_para_processar:
        try:
            driver.get(
                f"http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?pageheader=null&num_pt=&ano_pt=&nome_empreendedor=&cpf_cnpj_emprdor=&num_fob=&ano_fob=&cod_atividades=&cod_outros_municipios={number}&nome_empreendimento=&cpf_cnpj_emp=&tipoProcesso=&num_apefoutorga=&cod_empreendimento=&ano_apefoutorga="
            )
            lista_links_validos.append(driver.current_url) 

            # time.sleep(10)
        except TimeoutException:
            print(f"Tempo esgotado para carregar a página {number}, continuando para a próxima.")
        except Exception as e:
            print(f"Ocorreu um erro ao acessar a página {number}: {e}")


    # Marca o tempo de término
    end_time = time.time()

    # Calcula o tempo total de execução
    execution_time = end_time - start_time

    print(f"Tempo de execução: {execution_time / 60} minutos")

finally:
    # Fecha o navegador
    driver.quit()
