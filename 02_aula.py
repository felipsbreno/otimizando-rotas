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
driver.maximize_window()
driver.get("https://www.google.com/maps")

def Its_in_the_routes_tab():
    xpath = '//button[@aria-label="Fechar rotas"]'
    btn_routes = driver.find_elements(By.XPATH, xpath)
    return len(btn_routes) > 0

def add_destiny(address, num_box=1):    
    if not Its_in_the_routes_tab():
        inputAddress = driver.find_element(By.ID, 'searchboxinput')
        inputAddress.clear()
        inputAddress.send_keys(address)
        inputAddress.send_keys(Keys.RETURN)
    else:
        xpath = '//div[contains(@id, "directions-searchbox")]//input'
        box = driver.find_elements(By.XPATH, xpath)
        box = [c for c in box if c.is_displayed()] # verifica se as caixas para digitar estão sendo mostradas para os usuários
       
        if len(box) >= num_box:
            box_address = box[num_box-1]
            box_address.send_keys(Keys.CONTROL + 'a')
            box_address.send_keys(Keys.DELETE)
            box_address.send_keys(address)
            box_address.send_keys(Keys.RETURN)
        else:
            print(f'Não conseguimos adicionar o endereço {len(box)} | {num_box}')


def open_routes():
    xpath = '//button[@data-value="Rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    btn_routes = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    btn_routes.click()
  
    xpath = '//button[@aria-label="Fechar rotas"]'
    wait = WebDriverWait(driver, timeout=5)
    btn_routes = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

if __name__ == '__main__':
    address = [
                'Av. José Bonifácio, 245 - Farroupilha, Porto Alegre - RS, 90040-130', # Redenção
                'Av. Borges de Medeiros, 2035 - Menino Deus, Porto Alegre - RS, 90110-150', # Marinha
                'Av. Guaíba, 544 - Ipanema, Porto Alegre - RS, 91760-740', #Orla Ipanema
                'Av. Padre Cacique, 2000 - Praia de Belas, Porto Alegre - RS, 90810-180', #Iberê
              ]
    
    add_destiny(address[0], 1)
    open_routes()

    add_destiny(address[0], 1)
    add_destiny(address[1], 2)
    add_destiny(address[2], 3)
    add_destiny(address[3], 4)
    
    sleep(600)    