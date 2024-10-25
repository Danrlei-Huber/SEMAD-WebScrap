from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Configurações para o modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa o Chrome em modo headless
chrome_options.add_argument("--disable-gpu")  # Desativa o uso de GPU
chrome_options.add_argument("--no-sandbox")  # Necessário em alguns ambientes de servidor
chrome_options.add_argument("--disable-dev-shm-usage")  # Desativa o uso do /dev/shm
chrome_options.add_argument("--window-size=1920,1080")  # Tamanho da janela padrão
chrome_options.add_argument("--disable-extensions")  # Desativa extensões do navegador
chrome_options.add_argument("--disable-infobars")  # Desativa a barra de informações
chrome_options.add_argument("--remote-debugging-port=9222")  # Porta para depuração remota

# Inicializa o driver do Chrome com as opções configuradas
driver = webdriver.Chrome(options=chrome_options)

try:
    # Abre uma página
    driver.get("https://www.example.com")
    
    # Extrai o título da página
    title = driver.title
    print(f"Título da página: {title}")
    
finally:
    # Encerra a sessão do navegador
    driver.quit()