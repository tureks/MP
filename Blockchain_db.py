##### modul pro simulaci blockchainu - Blockchain_db.py
##### Autor: Štěpán Turek
#### Vkládání modulů
import sqlite3
import hashlib
from datetime import datetime
import json
import getpass
##### Definování tříd
class Wallet():
    def __init__(self, dbwallet):
        self.dbfile = dbwallet
        self.conn = sqlite3.connect(dbwallet)
        self.cur = self.conn.cursor()
        ##### vytvorime databazi blockchainu v pripade ze neexistuje
        self.cur.execute('''CREATE TABLE IF NOT EXISTS wallet
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            jmeno NOT NULL,
                            heslo NOT NULL
                        );''')
    def nahrat(self, dotaz, data=None):
        '''
        vložení do SQLite databaze s commitem
        '''    
        if data == None:
            self.cur.execute(dotaz)
        else:
            self.cur.execute(dotaz,data)
        self.conn.commit() # potvrzení změn
        return self.cur
    ### metoda pro vložení do databáze uživatelů
    def insert_wallet(self, data):
        '''
        ukládání dat do peněženky
        '''    
        ### vytvorime SQL prikaz
        query = "INSERT INTO wallet (jmeno, heslo)"
        query = query + "VALUES (?,?);"
        self.nahrat(query,data)
    ### metoda pro přihlášení do aplikace
    def prihlaseni(self): 
        '''
        Přihlášení do peněženky
        '''
        while True:
            print("Přihlášení")   
            print(50*"-") 
            jmeno = input("Zadejte uživatelské jméno: ")
            query = f"SELECT id, jmeno, heslo FROM wallet WHERE jmeno='{jmeno}';"
            overeni = self.nahrat(query).fetchone()
            row = overeni
            if overeni != None:
                row = self.nahrat(query).fetchone()
                id_uzivatele = row[0], row[1]
                heslo = row[2]
                zad_heslo = getpass.getpass("Zadejte heslo: ")
                zad_heslo = hashlib.sha256(zad_heslo.encode())
                zad_heslo = zad_heslo.hexdigest()
                if heslo == zad_heslo:
                    print (40*" ")
                    print (40*"-")
                    print (f"Vítejte {jmeno}")
                    print (40*"-")
                    break
            else:
                print("Zadali jste nesprávné jméno nebo heslo")
                opakovani = input("Přejete si zadávat znovu? A/N: ")
                volba = ["A","a"]
                if opakovani not in volba:
                    return False, False
        return True, id_uzivatele
    ### Vytvoření nového účtu
    def novy_uzivatel(self):
        """
        vytvoří profil nového uživatele
        """
        while True:
            jmeno = input("Zadejte uživatelské jméno: ")
            query = "SELECT jmeno FROM wallet"
            overeni = self.nahrat(query).fetchall()
            jmena = []
            for prvek in overeni:
                prvek = prvek[0]
                jmena.append(prvek)
            if jmeno not in jmena:
                heslo = getpass.getpass("Zadejte heslo: ")
                heslo = hashlib.sha256(heslo.encode())
                heslo = heslo.hexdigest()
                data = jmeno, heslo
                self.insert_wallet(data)
                break
            else:
                print("Toto uživatelské jméno již existuje")
        return 
    ### Metoda pro ukončení spojení s databází
    def __del__(self):
        """
        Uzavře spojení s databází
        """
        self.conn.close()
class Blockchain_databaze(object):
    def __init__(self, dbblockchain, id_uzivatele):
        self.dbblockchain = dbblockchain
        self.id_uzivatele = id_uzivatele
        self.ident, self.uzivatel = self.id_uzivatele
    def vytvoreni_blockchainu(self):
        """
        vytvoří databázi pro blockchain
        """
            ##### vytvorime databazi blockchainu v pripade ze neexistuje
        query = ('''CREATE TABLE IF NOT EXISTS zahlavi
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                verze NOT NULL,
                                predchozi_hash,
                                merkle_hash,
                                timestamp INTEGER NOT NULL,
                                target NOT NULL,
                                nonce NOT NULL
                            );''')
        self.sql(query)
        query = ('''CREATE TABLE IF NOT EXISTS transakce
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                seznam_transakci
                            );''')
        self.sql(query)
        query = ('''CREATE TABLE IF NOT EXISTS velikost
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                velikost_bloku INTEGER NOT NULL
                            );''')
        self.sql(query)
        query = ('''CREATE TABLE IF NOT EXISTS pocet
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                pocet_transakci NOT NULL
                            );''')
        self.sql(query)
        return
        ### metoda pro odeslání SQL dotazu
    def sql(self, dotaz, data=None):
        """
        vložení do SQLite databáze s commitem
        """
        conn = sqlite3.connect(self.dbblockchain)
        cursor = conn.cursor() 
        if data == None:
            cursor.execute(dotaz)
        else:
            cursor.execute(dotaz,data)
        conn.commit() # potvrzení změn
        return cursor
    def zjisteni_hashe(self):
        """
        vypočítá předchozí hash z předchozího bloku
        """
        max_id = self.kontrola()
        if max_id != False:
            query = f"SELECT verze, predchozi_hash, merkle_hash, timestamp, target, nonce FROM zahlavi WHERE id={max_id};"
            data = self.sql(query).fetchone()
            verze, predchozi_hash, merkle_hash, timestamp, target, nonce = data
            previous_hash = str(verze) + str(predchozi_hash) + str(merkle_hash) + str(timestamp) + str(target)
            previous_hash = hashlib.sha256(previous_hash.encode())
            previous_hash = int(previous_hash.hexdigest(), 16)
            previous_hash = str(previous_hash) + str(nonce)
            previous_hash = hashlib.sha256(previous_hash.encode())
            previous_hash = str(previous_hash.hexdigest())
        else: 
            previous_hash = "None"
        return previous_hash
        ### metoda pro vložení do databáze blockchainu
    def insert_zahlavi(self, data):
        """
        vložení záhlaví do blockchainu
        """
        ### vytvorime SQL prikaz
        query = "INSERT INTO zahlavi (verze, predchozi_hash, merkle_hash, timestamp, target, nonce)"         
        query = query + " VALUES (?,?,?,?,?,?);"
        self.sql(query,data)
    def insert_transakce(self, data):
        """
        vloží transakce do blockchainu
        """    
        data = [data]
        ### vytvorime SQL prikaz
        query = "INSERT INTO transakce (seznam_transakci)" 
        query = query + " VALUES (?);"
        self.sql(query, data)
    def insert_velikost(self, data):
        """
        vloží velikost bloku do blockchainu
        """ 
        ### vytvorime SQL prikaz
        data = [data]
        query = "INSERT INTO velikost (velikost_bloku)" 
        query = query + " VALUES (?);"
        self.sql(query,data)
    def insert_pocet(self, data):
        """
        vloží počet transakcí do blockchainu
        """   
        ### vytvorime SQL prikaz
        data = str(data)
        query = "INSERT INTO pocet (pocet_transakci)" 
        query = query + " VALUES (?);"
        self.sql(query,data)
        return
        ### metoda pro výpis databáze blockchainu
    def show(self):
        """
        zobrazí blockchain
        """
        query = "SELECT count(id) FROM zahlavi"
        pocet_bloku = self.sql(query).fetchone()
        pocet_bloku = pocet_bloku[0]
        id = 0
        while pocet_bloku > id:
            id += 1
            self.zobraz(id)
        return 
    def zobraz(self, id):
        """
        Zobrazí všechny prvky obsažené v jednom bloku
        """
        print ("")
        query = f"SELECT verze, predchozi_hash, merkle_hash, timestamp, target, nonce FROM zahlavi WHERE id={id}" 
        row = self.sql(query).fetchone()
        verze, predchozi_hash, merkle_hash, timestamp, target, nonce = row
        timestamp = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        print (70*"-") 
        print (f"# (Číslo bloku: {id})")   
        print (f"# Verze blockchainu: {verze}")
        print (f"# Hash předchozího bloku: {predchozi_hash}")
        print (f"# Kořen Merkleova stromu: {merkle_hash}")
        print (f"# Čas uzavření bloku: {timestamp}")
        print (f"# Target: {target}")
        print (f"# Nonce: {nonce}")
        query = f"SELECT seznam_transakci FROM transakce WHERE id={id}"
        row = self.sql(query).fetchone()
        if row != None:
            row = json.loads(row[0]) 
            for polozka in row:
                print(50*".")
                print (f"# Jméno autora:",polozka['odesilatel'])
                print (f"# Zpráva:",polozka['zprava'])
        else:
            print("Blok neobsahuje žádné transakce")
        print (50*"-")
        query = f"SELECT pocet_transakci FROM pocet WHERE id={id}" 
        row = self.sql(query).fetchone()
        row = row[0]
        print(f"# V tomto bloku je uloženo {row} záznamů")
        print (50*"-")
        query = f"SELECT velikost_bloku FROM velikost WHERE id={id}" 
        row = self.sql(query).fetchone()
        row = row[0]
        print(f"# Velikost bloku je {row} bytů")
        print (70*"-")
    def kontrola(self):
        """
        zjištění počtu záznamů v databázi
        """
        query= "SELECT MAX(id) FROM zahlavi"
        check = self.sql(query).fetchone()
        check = check[0]
        if check != None:
            return check
        else:
            return False
    def zjisteni_hashe(self):
        """
        vypočítá předchozí hash z předchozího bloku
        """
        max_id = self.kontrola()
        if max_id != False:
            query = f"SELECT verze, predchozi_hash, merkle_hash, timestamp, target, nonce FROM zahlavi WHERE id={max_id};"
            data = self.sql(query).fetchone()
            verze, predchozi_hash, merkle_hash, timestamp, target, nonce = data
            previous_hash = str(verze) + str(predchozi_hash) + str(merkle_hash) + str(timestamp) + str(target)
            previous_hash = hashlib.sha256(previous_hash.encode())
            previous_hash = int(previous_hash.hexdigest(), 16)
            previous_hash = str(previous_hash) + str(nonce)
            previous_hash = hashlib.sha256(previous_hash.encode())
            previous_hash = str(previous_hash.hexdigest())
        else: 
            previous_hash = "None"
        return previous_hash
    def search(self, max_id):
        """
        vyhledání bloku v blockchainu podle čísla bloku
        """
        print(f"Číslo posledního uloženého bloku je {max_id}")
        blok = int(input("Zadejte číslo hledaného bloku: "))
        print (50*"-")
        if blok <= max_id:
            self.zobraz(blok)
        else: 
            print ("Hledaný blok nebyl nalezen")
######## KONEC