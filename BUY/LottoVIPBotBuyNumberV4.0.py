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
import ast
gc = gspread.service_account(filename='creds.json')

delay = ''


class LottoVIP:
    def __init__(self, username, password):

        self.session = requests.Session()
        response = self.session.get("https://www.lottovip.com/login").headers
        self.csrf_token = response['Set-Cookie'].split(";")[6].split("=")[1]
        data = {"csrf_token": self.csrf_token, "login": "1",
                "username": username, "password": password}
        self.session.post("https://www.lottovip.com/login", data=data)

    def check_balance(self):
        return float(self.session.get("https://www.lottovip.com/member/credit_balance").text)

    def checkroom(self):  # ห้องแรกที่แทงได้
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
                return h[1].rsplit('/', 1)[-1].replace('">', "")

    def buy(self, room_id, price, last_add_num=0):
        sh = gc.open('NumberAPI').sheet1
        F2 = sh.get("F2")[0][0]
        F6 = sh.get("F6")[0][0]
        F2toList = ast.literal_eval(F2)
        F6toList = ast.literal_eval(F6)
        print("F2", F2toList)
        print("F6", F6toList)
        print("F2", type(F2toList))
        print("F6", type(F6toList))
        payNinety = F2toList
        payNinetyTwo = F6toList
        last_add_num = 0
        poy = {
            "bet_id": str(room_id),
            "poy_list": [],
            "note": ""
        }
        if(len(payNinetyTwo) != 0):
            for x in payNinetyTwo:
                last_add_num += 1
                option = {
                    "option": "teng_bon_2",
                    "number": x,
                    "price": int(price),
                    "multiply": "92.00",
                    "is_duplicate": False,
                    "last_add_num": last_add_num
                }
                poy['poy_list'].append(option)
        if(len(payNinety) != 0):
            for x in payNinety:
                last_add_num += 1
                option = {
                    "option": "teng_bon_2",
                    "number": x,
                    "price": int(price),
                    "multiply": "90.00",
                    "is_duplicate": False,
                    "last_add_num": last_add_num
                }
                poy['poy_list'].append(option)
        encode1 = json.dumps(poy)
        encode2 = json.dumps(encode1)
        # print("ENNNNNNNNNNNCODE", json.loads(encode2))
        f = self.session.post(
            ' https://www.lottovip.com/send_poy', data={"poy": json.loads(encode2)})
        return f.json(), payNinety + payNinetyTwo

    def check_poy(self, poyid):  # 0 lose, 3 wait , 1 win
        print("POY ID = ", poyid)
        try:
            poy_detail = self.session.get(
                "https://www.lottovip.com/member/poy/detail/"+poyid)
            Element_html = html.fromstring(poy_detail.content)
            reelement = Element_html.xpath(
                '/html/body/div[3]/div[2]/div/div[3]/div[2]/div[3]')[0]
            for x in reelement:
                h = etree.tostring(x[0][2], method='html', with_tail=False)
                print("HHHHHHHHHHHH", h)
                if b'poy-status notyet' in h:
                    return 3
                if b'poy-status win' in h:
                    return 1
            return 0
        except:
            return 4

    def mixedOptions(self, num):  # 1 = B mix C ; 2 = C mix B
        allnum = []
        try:
            sh = gc.open('NumberAPI').sheet1
            numberB = sh.get("B2")[0][0]
            numberC = sh.get("C2")[0][0]
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
        print(type(allNumBuy))
        print(type(limitNinety))
        payNinetyTwo = allNumBuy
        mixNum = allNumBuy + limitNinety
        payNinety = [item for item, count in collections.Counter(
            mixNum).items() if count > 1]

        payNinetyTwo = allNumBuy
        for numPayNinety in payNinety:
            payNinetyTwo.remove(numPayNinety)
        return [payNinety, payNinetyTwo]


def main():
    username = input("USERNAME :").strip()
    password = input("PASSWORD :").strip()
    bet = int(input("BET BAHT :"))
    take_profit = int(input("TP BAHT :"))
    multi_matingale = int(input("multi matingale :"))
    sec = float(input("Delay (Sec):"))
    delay = sec
    bet_ma = bet
    check_win = 0
    check_loose = 0
    check_mtg = 0
    lotto = LottoVIP(username, password)
    balance = lotto.check_balance()
    money_profit = lotto.check_balance()
    os.system("cls")
    print("BALANCE BAHT: "+str(money_profit) +
          "  PROFIT BAHT: "+str(money_profit - balance))
    print("WIN : "+str(check_win)+"  LOSE : "+str(check_loose))
    if balance < bet:
        os.system("cls")
        print("Your balance is not enough.")
    else:
        while True:
            num_room = lotto.checkroom()
            buy_num, buyNumLen = lotto.buy(num_room, bet_ma)
            while True:
                checkPoy = lotto.check_poy(buy_num["poy_id"])
                money_profit = lotto.check_balance()
                if (money_profit - balance) >= take_profit:
                    while True:
                        os.system("cls")
                        print("All Num Buy : ", buyNumLen)
                        print("Total : ", len(buyNumLen), " Numbers")
                        print("BALANCE BAHT: "+str(money_profit) +
                              "  PROFIT BAHT: "+str(money_profit - balance))
                        print("WIN : "+str(check_win) +
                              "  LOSE : "+str(check_loose))

                        print("Start delay : %s" % time.ctime())
                        time.sleep(60)
                        print("End delay : %s" % time.ctime())
                os.system("cls")
                print("BALANCE BAHT: "+str(money_profit) +
                      "  PROFIT BAHT: "+str(money_profit - balance))
                print("WIN : "+str(check_win)+"  LOSE : "+str(check_loose))
                print("All Num Buy : ", buyNumLen)
                print("Total : ", len(buyNumLen), " Numbers")
                if checkPoy == 1:
                    check_win += 1
                    bet_ma = bet
                    check_mtg = 0
                    break
                elif checkPoy == 0:
                    check_loose += 1
                    bet_ma *= multi_matingale
                    check_mtg += 1
                    break
                elif checkPoy == 3:
                    print("Checkpoy Notyet wait...")
                elif checkPoy == 4:
                    os.system("cls")
                    print("error Func checkPoy")
                print("Start delay : %s" % time.ctime())
                time.sleep(delay)
                print("End delay : %s" % time.ctime())


if __name__ == "__main__":
    main()
