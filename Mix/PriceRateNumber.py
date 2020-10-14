import requests
from lxml import html
from lxml import etree
import json
import random
import os
import time
from bs4 import BeautifulSoup
import gspread
import collections
import re

gc = gspread.service_account(filename='creds.json')

delay = ''


class PriceRateNumber:
    def __init__(self, username, password):
        self.sh = gc.open('NumberAPI').sheet1
        self.session = requests.Session()
        response = self.session.get("https://www.lottovip.com/login").headers
        self.csrf_token = response['Set-Cookie'].split(";")[6].split("=")[1]
        data = {"csrf_token": self.csrf_token, "login": "1",
                "username": username, "password": password}
        self.session.post("https://www.lottovip.com/login", data=data)

    def mixedOptions(self, num):
        allnum = []
        try:

            numberB = self.sh.get("B2")[0][0]
            numberC = self.sh.get("C2")[0][0]
            if(num == 1):
                for x in numberB:
                    for y in numberC:
                        allnum.append(x+y)
                return allnum
            elif(num == 2):
                for x in numberC:
                    for y in numberB:
                        allnum.append(x+y)
                return allnum
            else:
                return allnum
        except:
            print('Error')
            return allnum

    def limitNumber(self):
        sa = []
        limitNum = []
        room_detail = self.session.get(
            'https://www.lottovip.com/member/lottery/yeekee')
        Element_html = html.fromstring(room_detail.content)
        reelement = Element_html.xpath(
            '/html/body/div[3]/div[2]/div[1]/div[3]/div[2]/div/div')[0]

        for x in reelement:
            h = str(etree.tostring(x, method='html',
                                   with_tail=False)).split("\\n")
            if "close" in h[2]:
                pass
            else:
                h[1].rsplit('/', 1)[-1].replace('">', "")
                sa.append(h[1].rsplit('/', 1)[-1].replace('">', ""))

        room = self.session.get(
            'https://www.lottovip.com/member/lottery/yeekee/'+sa[0])
        soup = BeautifulSoup(room.content, 'html5lib')
        scripts = soup.find_all('script', text=re.compile(
            "var bet_list_detail = "))[0].get_text()
        a = re.findall("\'.*\'", scripts)[0]
        b = a.replace("'", "")
        jsonData = json.loads(b)
        limit = jsonData['limit']
        for x in limit:
            a = dict([(k, v)
                      for k, v in x.items() if x["option"] == "teng_bon_2"])
            if(len(a) > 0):
                numStrip = a["number"].strip()
                if(int(numStrip) > 9):
                    limitNum.append(str(numStrip))
        return limitNum

    def payRate(self, formulaNum):
        allNumBuy = formulaNum
        limitNinety = self.limitNumber()
        # print(type(allNumBuy))
        # print(type(limitNinety))
        payNinetyTwo = allNumBuy
        mixNum = allNumBuy + limitNinety
        payNinety = [item for item, count in collections.Counter(
            mixNum).items() if count > 1]
        print("All buy num : ", len(allNumBuy), " 's")
        print("Pay 90  = ", payNinety,
              "amount ", len(payNinety), " 's")
        payNinetyTwo = allNumBuy
        for numPayNinety in payNinety:
            payNinetyTwo.remove(numPayNinety)
        print("Pay 92 =  ", payNinetyTwo,
              "amount ", len(payNinetyTwo), " 's")
        self.sh.update('F2', str(payNinety))
        self.sh.update('F6', str(payNinetyTwo))


def main():
    username = input("USERNAME : ").strip()
    password = input("PASSWORD : ").strip()
    sec = float(input("Delay (Sec): "))
    numMix = int(input("Mixed (1 = B mix C , 2 = C mix B) : "))
    delay = sec
    priceRate = PriceRateNumber(username, password)
    while True:
        num_formula = priceRate.mixedOptions(numMix)
        priceRate.payRate(num_formula)
        time.sleep(delay)


if __name__ == "__main__":
    main()
