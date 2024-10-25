from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.chrome.options import Options

# URL do Hub do Selenium Grid
SELENIUM_GRID_URL = "http://localhost:4444"

# Configurando as opções do navegador
chrome_options = Options()
#chrome_options.add_argument('--headless')  # Executar sem interface gráfica, opcional
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

def scrape(url):
    # Conecte-se ao Selenium Grid com as capacidades definidas
    driver = webdriver.Remote(command_executor=SELENIUM_GRID_URL, options=chrome_options)
    
    # Acesse a URL
    driver.get(url)
    
    # Faça o scraping desejado (exemplo: obter o título da página)
    title = driver.title
    
    # Feche o navegador
    driver.quit()
    
    return title

# Lista de URLs para scraping
urls = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3",
    # Adicione mais URLs conforme necessário
]

# Usar ThreadPoolExecutor para paralelizar
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(scrape, urls)

# Exibir os resultados
for result in results:
    print(result)
