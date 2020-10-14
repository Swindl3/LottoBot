import gspread
import requests
from bs4 import BeautifulSoup
from time import sleep
import os

gc = gspread.service_account(filename='creds.json')


s = requests.Session()

delay = ''


class NumberSC:
    def __init__(self, username, password):
        try:
            url = "https://www.vgetrich.com/login"
            r = s.get(url)
            # print(r.content)
            soup = BeautifulSoup(r.content, 'lxml')
            _token = soup.find('input', attrs={'name': '_token'})['value']
            loginData = {
                '_token': _token,
                'phone': username,
                'password': password,
                'remember': 'on'
            }
            r = s.post('https://www.vgetrich.com/login', data=loginData)
        except:
            print("Login Error !")

    def getNumberSC(self):
        sh = gc.open('NumberAPI').sheet1
        try:
            r = s.get('https://www.vgetrich.com/my-favorite/lottovip')
            soup = BeautifulSoup(r.content, 'lxml')
            table = soup.findAll("table")
            table_one = table[0]("td")[-1].get('data-number')
            table_two = table[1]("td")[-1].get('data-number')

            sh.update('B1', table[0]['id'])
            sh.update('C1', table[1]['id'])
            sh.update('B2', table_one)
            sh.update('C2', table_two)
            return print('Table  ID : ' + table[0]['id'] + '  Value : ' + table_one + '\n'
                         'Table ID : ' + table[1]['id'] + '  Value : ' + table_two + '\n')
        except:
            print("Get data Error !")
            sh.update('B1', '')
            sh.update('C1', '')
            sh.update('B2', '')
            sh.update('C2', '')


if __name__ == "__main__":
    username = input("Username : ").strip()
    password = input("Password : ").strip()
    sec = float(input("Delay (Sec):"))
    delay = sec
    sc = NumberSC(username, password)
    while True:
        print("Starting...")
        sc.getNumberSC()
        sleep(delay)
        # os.system("cls")
