from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep

service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(2)
driver.get("https://www.google.com/maps")

def add_destiny(address):
    inputSerachAddress = driver.find_element(By.ID, 'searchboxinput')
    inputSerachAddress.clear()
    inputSerachAddress.send_keys(address)
    inputSerachAddress.send_keys(Keys.RETURN)

def open_routes():
    xpath = "//button[@data-value='Rotas']"
    wait = WebDriverWait(driver, timeout=5)
    btn_routes = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    btn_routes.click()

    xpath = "//button[@aria-label='Fechar rotas']"
    wait = WebDriverWait(driver, timeout=5)
    btn_routes = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

if __name__ == '__main__':
    address = 'Av. José Bonifácio, 245 - Farroupilha, Porto Alegre - RS, 90040-130' # Redenção
    add_destiny(address=address)
    open_routes()
    sleep(600)    