from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# CONFIGURAÇÕES DO SELENIUM
# Define o tempo máximo para carregar uma página
driver.set_page_load_timeout(120)


for i in range(1, 860):
    try:
        link_municipio = f"http://www.siam.mg.gov.br/siam/processo/processo_emprto_emprdor.jsp?pageheader=null&num_pt=&ano_pt=&nome_empreendedor=&cpf_cnpj_emprdor=&num_fob=&ano_fob=&cod_atividades=&cod_outros_municipios={i}&nome_empreendimento=&cpf_cnpj_emp=&tipoProcesso=&num_apefoutorga=&cod_empreendimento=&ano_apefoutorga="
        driver.get(link_municipio)

        span_element = driver.find_elements(By.CSS_SELECTOR, "span.OraHeader")[1]
        municipio = span_element.text.strip()
        num_processos = driver.find_element(By.XPATH, "//span[contains(@class, 'UptInputHeader')]").text

        print(f"## ID: {i} || cidade: {municipio} || num de processos: {num_processos}")
    except:
        print(f"## erro ao processar o ID: {i} ")


