from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from time import sleep
import pulp
import itertools

service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(2)
driver.maximize_window()
driver.get("https://www.google.com/maps")

def sleep_before_interactive(time = 2):
    return sleep(time)

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

def add_more_destiny():
    xpath = '//*[@id="omnibox-directions"]/div/div[3]/button/div[2]/span'
    wait = WebDriverWait(driver, timeout=3)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))

    btn_add_more_destiny = driver.find_element(By.XPATH, xpath)
    btn_add_more_destiny.click()

def select_type_condution(type_condution = 'Carro'):
    xpath = f'//img[@aria-label="{type_condution}"]'
    wait = WebDriverWait(driver, timeout=3)
    btn_select_type_condution = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    btn_select_type_condution.click()

def return_time_total():
    xpath = '//*[@id="section-directions-trip-0"]//div[contains(text(), "min")]'
    wait = WebDriverWait(driver, timeout=3)
    time_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return int(time_element.text.replace(' min', ''))

def return_distance_total():
    xpath = '//*[@id="section-directions-trip-0"]//div[contains(text(), "km")]'
    wait = WebDriverWait(driver, timeout=3)
    time_element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    return float(time_element.text.replace(' km', '').replace(',', '.'))


# =========================== Funções Principais ===============================================

def generate_pares_distance(address):
    distance_pares = {}
    driver.get("https://www.google.com/maps")
    add_destiny(address[0], 1)
    open_routes()
    select_type_condution(type_condution="Carro")

    for i, end1 in enumerate(address):
        add_destiny(end1, 1)
        for j, end2 in enumerate(address):
            if i != j:
                add_destiny(end2, 2)
                time_par = return_time_total()
                distance_pares[f'{i}_{j}'] = time_par

    return distance_pares


def generate_optimize(address, distance_pares):
    def distance(end1, end2):
        return distance_pares[f'{end1}_{end2}']
    
    prob = pulp.LpProblem('TSP', pulp.LpMinimize)
    x = pulp.LpVariable.dicts('x', [(i, j) for i in range(len(address)) for j in range(len(address)) if i != j], cat='Binary')
    prob += pulp.lpSum([distance(i, j) * x[(i, j)] for i in range(len(address)) for j in range(len(address)) if i != j])

    # Restrição para entrar e sair uma vez da cidade
    for i in range(len(address)):
        prob += pulp.lpSum([x[(i, j)] for j in range(len(address)) if i != j]) == 1
        prob += pulp.lpSum([x[(j, i)] for j in range(len(address)) if i != j]) == 1

    # Restrição para evitar subturs
    for k in range(len(address)):
        for S in range(2, len(address)):
            for subset in itertools.combinations([i for i in range(len(address)) if i != k], S):
                prob += pulp.lpSum([x[(i, j)] for i in subset for j in subset if i != j]) <= len(subset) - 1

    prob.solve(pulp.PULP_CBC_CMD())
    solved = []
    init_city = 0
    next_city = init_city

    while True:
        for j in range(len(address)):
            if j != next_city and x[(next_city, j)].value() == 1:
                solved.append((next_city, j))
                next_city = j
                break
        if next_city == init_city:
            break
   
    print("Rota:")
    for i in range(len(solved)):
        print(solved[i][0], ' ->> ', solved[i][1])

    return solved

def show_route_aoptimize(address, solution):
    driver.get("https://www.google.com/maps")

    add_destiny(address[0], 1)
    open_routes()

    for i in range(len(solution)):
        add_destiny(address[solution[i][0]], i+1)
        add_more_destiny()
    
    add_destiny(address[0], len(address) + 1)


if __name__ == '__main__':
    address = [
                'Av. José Bonifácio, 245 - Farroupilha, Porto Alegre - RS, 90040-130', # Redenção
                'AVENIDA EDVALDO PERREIRA PAIVA 3001 - Praia de Belas, Porto Alegre - RS, 91110-060', # Marinha
                'Av. Guaíba, 544 - Ipanema, Porto Alegre - RS, 91760-740', #Orla Ipanema
                'Av. Padre Cacique, 2000 - Praia de Belas, Porto Alegre - RS, 90810-180', #Iberê
                'R. Dr. Salvador França, 1427 - Jardim Botânico, Porto Alegre - RS, 90690-000' # Jardim Botânico
              ]
    
    distance_pares = generate_pares_distance(address)
    solved = generate_optimize(address, distance_pares)
    show_route_aoptimize(address, solved)
    
    sleep_before_interactive(time=600)    