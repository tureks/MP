##### Aplikace pro simulaci blockchainu
##### Autor: Štěpán Turek
#### Vložení modulů
from Blockchain_db import *
import hashlib
from datetime import datetime
import sys
import json
##### Nastavení proměnných
verze_blockchainu = 1.0
dbwallet = "wallet.db"
dbblockchain = "blockchain.db"
######## Deklarace tříd
class Blockchain(object):
    def __init__(self):
        self.aplikace = App()
        self.transakce = []
    # vložení jednoho záznamu 
    def pridej_transakci(self):
        """
        vložení transakce
        """
        ######## VKLADANI DAT
        zprava = input("Zadejte zprávu: ")
        ident, autor = id_uzivatele 
        data = {
            "id":ident,
            "odesilatel":autor,
            "zprava":zprava,
        }
        self.transakce.append(data)
        print(self.transakce)
    def merkle_tree(self):
        """
        rozdělení transakcí do merkleova stromu
        """
        merkle_hash = self.hash_dva(self.transakce)
        velikost = len(merkle_hash)
        if velikost == 1:
            merkle_hash = merkle_hash[0]
            return merkle_hash
        elif velikost == 0:
            merkle_hash = "None"
        else:
            while velikost > 2:
                self.hash_dva(merkle_hash)
            return merkle_hash
    def hash_dva(self, seznam):
        """
        zahashování párů
        """
        delka = len(seznam)
        modulo = delka%2
        if modulo == 1:
            seznam.append(seznam[0])
            delka = len(seznam)
        polozka1 = 0
        polozka2 = 1
        novy_seznam = []
        while delka != 0:
            delka -= 2
            spojeni = str(seznam[polozka1]) + str(seznam[polozka2])
            spojeni = hashlib.sha256(spojeni.encode())
            spojeni = spojeni.hexdigest()
            polozka1 += 1
            polozka2 += 1
            novy_seznam.append(spojeni)
        return novy_seznam
    def priprava_bloku(self):
        """
        Připraví blok a následně jej uloží do blockchainu
        """
        predchozi_hash = block_db.zjisteni_hashe()
        timestamp = datetime.now()
        timestamp = datetime.timestamp(timestamp)
        timestamp = round(timestamp)
        merkle_root = self.merkle_tree()
        nonce = self.tezba(predchozi_hash)
        data = verze_blockchainu, predchozi_hash, str(merkle_root), timestamp, hex(self.target), nonce
        block_db.insert_zahlavi(data)
        dotaz = json.dumps(self.transakce)
        block_db.insert_transakce(dotaz)
        pocet = len(self.transakce)
        block_db.insert_pocet(pocet)
        polozky = data, self.transakce, pocet
        velikost = sys.getsizeof(polozky)
        block_db.insert_velikost(velikost)
        self.transakce = []
        return print(f"Blok byl přidán do blockchainu")
    def merkle_tree(self):
        """
        rozdělení transakcí do merkleova stromu
        """
        seznam = []
        for polozka in self.transakce:
            seznam.append(polozka)
        merkle_hash = self.hash_dva(seznam)
        velikost = len(merkle_hash)
        if velikost == 1:
            merkle_hash = merkle_hash[0]
            return merkle_hash
        elif velikost == 0:
            merkle_hash = "None"
        else:
            while velikost > 2:
                self.hash_dva(merkle_hash)
            return merkle_hash
    def hash_dva(self, seznam):
        """
        zahashování párů
        """
        delka = len(seznam)
        modulo = delka%2
        if modulo == 1:
            print(self.transakce)
            seznam.append(seznam[0])
            print(self.transakce)
            delka = len(seznam)
        polozka1 = 0
        polozka2 = 1
        novy_seznam = []
        while delka != 0:
            delka -= 2
            spojeni = str(seznam[polozka1]) + str(seznam[polozka2])
            spojeni = hashlib.sha256(spojeni.encode())
            spojeni = spojeni.hexdigest()
            polozka1 += 1
            polozka2 += 1
            novy_seznam.append(spojeni)
        return novy_seznam
    
    def tezba(self, block_hash):
        """
        Proof-of-Work metoda spojená s uzavíráním bloku
        """
        obtiznost = 14
        self.target = int(2 ** (256 - obtiznost)) 
        nonce=0
        if block_hash == "None":
            block_hash = ""
        nonce_hash = block_hash + str(nonce)
        nonce_hash = hashlib.sha256(nonce_hash.encode())
        nonce_hash = nonce_hash.hexdigest()
        nonce_hash = int(nonce_hash, 16)
        while nonce_hash > self.target:
            nonce += 1
            # print (nonce)
            nonce_hash = block_hash + str(nonce)
            nonce_hash = hashlib.sha256(nonce_hash.encode())
            nonce_hash = nonce_hash.hexdigest()
            nonce_hash = int(nonce_hash, 16)           
        print (f"Nalezený hash: {hex(nonce_hash)}")
        print (f"Nalezená nonce: {nonce}")
        o_nonce = self.overeni_nonce(self, nonce)
        if o_nonce == True:
            print ("Nonce schválena")
            return (nonce)
        else:
            print("Nonce nebyla ověřena")
            self.aplikace.run()
    def overeni_nonce(self, block_hash, nonce):
        """
        Ověří správnost nonce, simulace ostatních uživatelů
        """
        nonce_hash = str(block_hash) + str(nonce)
        nonce_hash = hashlib.sha256(nonce_hash.encode())
        nonce_hash = int(nonce_hash.hexdigest(), 16)
        if nonce_hash > self.target:
            overeni = True
        else:
            overeni = False
        return overeni
class App(object):   

    """
      Třída aplikace pro práci s blockchainem
    """
    def menu(self):
        """
        Funkce pro vytisknutí menu a vybrání volby
        """
        volby = ["P","V","Z","U","B"]
        volba = ''
        while (not volba in volby):
            print ("\n      MENU")
            print (30 * "-")
            print ("  P ... Uložit záznam")
            print ("  B ... Uzavřít blok")
            print ("  V ... Vyhledat blok v blockchainu")
            print ("  Z ... Zobrazit blockchain")
            print ("  U ... Ukončit aplikaci")
            volba = input("Zadejte svou volbu: ")
            volba = volba.upper()
        return volba 
    # hlavní programová smyčka
    def run(self): # přidat funkci pro uzavírání bloku založenou na čase a pravděpodobnosti
        """
          Hlavní programová smyčka
        """
        ##### PROGRAMOVA SMYCKA
        while True:
            #### vypsani menu a odchytneme volbu 
            volba = self.menu()
            if (volba == 'Z'):
                zkontroluj = block_db.kontrola()
                if zkontroluj == False:
                    print ("V blockchainu není uveden žádný záznam")
                else:
                    block_db.show()
            elif (volba == 'V'):
                zkontroluj = block_db.kontrola()
                if zkontroluj == False:
                    print ("V blockchainu není uveden žádný záznam")
                else:
                    block_db.search(zkontroluj)
            elif (volba == 'P'):
                blockchain.pridej_transakci()
            elif (volba == 'B'):
                blockchain.priprava_bloku()
            else:
                #### ukoncime aplikaci
                penezenka.__del__()
                print ("Na shledanou.")
                break
######### HLAVNÍ PROGRAM #########
if __name__ == "__main__":
    print("Poznámkový blok založený na blockchainu")
    print (50*"-")
    blockchain = Blockchain()
    penezenka = Wallet(dbwallet)
    aplikace = App()
    uzivatel = input("Chcete přidat nového uživatele? A/N: ")
    print (50*" ")
    volba = ["A", "a"]
    if uzivatel in volba:
        penezenka.novy_uzivatel()
    overeni, id_uzivatele = penezenka.prihlaseni()
    if overeni == True:
        block_db = Blockchain_databaze(dbblockchain, id_uzivatele)
        #vytvoření databáze pro ukládání blockchainu pokud stále neexistuje
        block_db.vytvoreni_blockchainu()
        aplikace.run()
    #### Ukončení programu
    print("Simulace blockchainu ukončena")
    exit()
###### KONEC ######