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

links = []
links.append("http://www.siam.mg.gov.br/siam/empreendedor/consultar_list.jsp?pageheader=N&num_pt=00426&ano_pt=1996&num_pa=001&ano_pa=1996&num_proc_administrativo=001&ano_proc_administrativo=1996&cod_empreendimento=23922&cod_empreendedor=1145&tipoProcesso=1")
links.append("http://www.siam.mg.gov.br/siam/empreendedor/consultar_list.jsp?pageheader=N&num_pt=00367&ano_pt=1995&num_pa=002&ano_pa=2002&num_proc_administrativo=002&ano_proc_administrativo=2002&cod_empreendimento=24148&cod_empreendedor=2965&tipoProcesso=1")
links.append("http://www.siam.mg.gov.br/siam/empreendedor/consultar_list.jsp?pageheader=N&num_pt=00036&ano_pt=2002&num_pa=001&ano_pa=2002&num_proc_administrativo=001&ano_proc_administrativo=2002&cod_empreendimento=14007&cod_empreendedor=7614&tipoProcesso=1")
links.append("http://www.siam.mg.gov.br/siam/empreendedor/consultar_list.jsp?pageheader=N&num_pt=02588&ano_pt=2002&num_pa=003&ano_pa=2013&num_proc_administrativo=003&ano_proc_administrativo=2013&cod_empreendimento=24354&cod_empreendedor=8663&tipoProcesso=1")
links.append("http://www.siam.mg.gov.br/siam/empreendedor/consultar_list_ief.jsp?pageheader=N&num_pt=22391&ano_pt=2012&num_pa=001&ano_pa=2013&num_proc_administrativo=001&ano_proc_administrativo=2013&cod_empreendimento=703694&cod_empreendedor=589776&tipoProcesso=1")


def main():
    link_pdfs_validos = []
    link_pdfs_nao_validos = []
    DATA_INICIO_PDFS_VALIDOS = 2019

    try:
        print("# Processando links...")
        for link in links:
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
                    link_pdfs_validos.append(f"{url_limpa};{td_texts[0]};{td_texts[1]};{td_texts[3]};{td_texts[2]}")
                else: 
                    link_pdfs_nao_validos.append(f"{url_limpa};{td_texts[0]};{td_texts[1]};{td_texts[3]};{td_texts[2]}")

        print("urls (links validos) limpas")
        for l in link_pdfs_validos:
            print(l)
        print("urls (links nao validos) limpas")
        for l in link_pdfs_nao_validos:
            print(l)


    except Exception as e:
        print(f"# houve um errro: {e}")



if __name__ == "__main__":
    main()