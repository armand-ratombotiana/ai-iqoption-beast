import shutil
from colorama import Fore, init
import iqoptionapi
from iqoptionapi.stable_api import IQ_Option
from datetime import datetime, timedelta
import time
import pandas as pd
import pandas_ta as ta
import ta as ta_ta
import functools
import os
import platform
import random
from constants import ACTIVES


class TRADING:
    def __init__(self, email, password, profit_attendu, mise_type="normal", account_type="demo", max_losses=10,direction="BUY",
                 profit_par_pair=3, initial_amount=1, martingal_factor=2.2):
        self.email = email
        self.payout = 0.85
        self.password = password
        saisie = input("\033[0mStop loss : \033[95m").strip()
        if saisie:
            self.stop_loss = int(saisie)  # Convertir en entier si une valeur est entrée
        else:
            self.stop_loss = 1000000  # Valeur par défaut
        #self.stop_loss = int(input("\033[0mStop loss : \033[95m"))
        self.initial_amount = initial_amount
        self.amount = initial_amount
        self.solde_init_ = 0
        self.solde_act_ = 0
        self.total_profit = 0
        self.point = 0
        self.date_open = None
        self.date_close = None
        self.profit_attendu = profit_attendu
        self.profit_par_pair = profit_par_pair
        self.profit_in_paire = 0
        self.search_signal = True
        self.croisement = None
        self.is_perturbe = False
        self.api = None
        self.instrument = None
        self.action_detected = None
        self.last_signal = direction
        self.losses = 0
        self.paires_list = []
        self.pairs_for_trade = []
        self.martingal_factor = martingal_factor
        self.is_loss = False
        self.is_renverse = False
        self.nb_recup = 0
        self.nb_trade_losses = 0
        self.total_perte = 0
        self.in_simu = False
        self.suiv = False
        self.demarrage = True
        self.in_trade = True
        self.max_losses = max_losses
        self.mise_type = mise_type
        self.account_type = account_type
        self.mises = [1, 2.176, 4.736, 10.308, 22.435, 48.829, 106.275, 231.305, 503.428, 1095.696]
        #self.mises = [5.5, 17.3, 42.0, 94.3, 204.65, 440, 814, 1505.89, 2785.9, 5153.91]
        #self.mises = [5.5, 17.3, 42.0, 94.3, 5.5, 17.3, 42.0, 94.3 ,5.5, 17.3, 42.0, 94.3]
        self.mise_recup = [1, 1.176, 2.56, 5.572, 12.127, 26.394, 57.446, 125.029, 272.122, 592.266]
        self.time_expired_dot = 0
        self.stop_date = datetime(2025, 2, 5)
        self.current_color = None
        self.conn = True
        self.back_into = True
        self.back_into_signal = True
        self.sa = True
        if self.mise_type == "zero":
            self.mises = self.mise_recup

    def reset_mises(self, solde_actuel, payout):
        self.mises = [round((solde_actuel * (i / 100))/payout, 2) for i in range(1, 11)]

    def get_payout(self, pair):
        instrument_type = "digital"
        try:
            payout = self.api.get_digital_payout(pair) if instrument_type == "digital" else self.api.get_binary_payout(pair)
            return payout if payout else 0
        except Exception as e:
            #print(f"Erreur lors de la récupération du payout pour {pair} : {e}")
            return 0

    def reconnect_on_failure(func):
        """Décorateur pour gérer la reconnexion automatique en cas d'échec"""

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            for attempt in range(100):  # Nombre de tentatives avant l'arrêt
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    print(f"Erreur : {e}, tentative de reconnexion ({attempt + 1}/100)...", end="\r")
                    self.handle_reconnection()
                    time.sleep(15)  # Attente avant de réessayer
            raise Exception("Échec de la reconnexion après plusieurs tentatives.")

        return wrapper

    @reconnect_on_failure
    def connect_to_iq_option(self,s=0):
        """ Connexion à l'API IQ Option """
        #print(f"eto1")
        self.api = IQ_Option(self.email, self.password)
        connect_result, connect_message = self.api.connect()
        #print(f"connect_result : {connect_result}  , connect_message : {connect_message}")

        while not connect_result:

            # Nettoyer l'écran
            print("\033[2J\033[H", end="")
            if platform.system() == 'Windows':
                os.system('cls')
            else:
                os.system('clear')
            print("\n\033[91m🔴Erreur de connexion! Veuillez verifier votre connexion internet ou votre informations\033[0m")
            self.email = input("\033[0mEmail : \033[95m")
            self.password = input("\033[0mPassword : \033[95m")
            print("\033[0m")
            self.api = IQ_Option(self.email, self.password)
            connect_result, connect_message = self.api.connect()
        print("\033[92mConnexion reussie...\033[0m")
        if s == 0:
            #self.mis_a_jour_des_actifs()
            print("\n\033[94mLISTE DES PAIRS DISPONNIBLES:\033[0m")
            pairs = []
            self.solde_init_ = self.api.get_balance()
            self.solde_act_ = self.api.get_balance()
            pairs = self.get_open_digital_markets()
            #pairs = self.get_open_digital_markets_digital()
            if pairs:
                self.choose_pair_to_trade(pairs)
            else:
                print("Aucune paire disponible pour trader.")
            if self.account_type == "real":
                self.api.change_balance("REAL")  # Utilisation du compte reel
            else:
                self.api.change_balance("PRACTICE")  # Utilisation du compte démo
        return True


    def ensure_connection(self,r=0):
        """ Vérifie et rétablit la connexion si elle est perdue """
        t = True
        while not self.api.check_connect():
            self.is_perturbe = True
            if t:
                print("\033[91m⚠️ Connexion perdue ! Tentative de reconnexion...\033[0m")
                t = False
            self.api.connect()
            time.sleep(5)  # Attendre 5 secondes avant de réessayer
        if r == 1:
            if self.is_perturbe:
                self.is_perturbe = False
                print("\033[92m✅ Connexion rétablie !\033[0m")
                etat = input("\033[0mEtat du trade (arrêter/continuer/reprendre_0) ? : \033[0m")
                if etat == "arrêter":
                    print("\033[94m🔴 Le robot s'arrête dans 5s...\033[0m")
                    time.sleep(5)
                    exit()
                elif etat == "reprendre_0":
                    self.losses = 0
                    self.is_loss = False
                    self.last_signal = None
                    self.demarrage = True


    def choose_pair_to_trade(self, pairs):
        """ Permet à l'utilisateur de choisir une paire à trader """
        pairs = sorted(pairs)
        print("\n\033[94mSélectionnez une paire pour trader :\033[0m")
        for i, pair in enumerate(pairs):
            print(f"{i + 1}. {pair}    => payout : {self.get_payout(pair)} ")

        while True:
            try:
                choix = int(input("\nEntrez le numéro de la paire choisie : ")) - 1
                if 0 <= choix < len(pairs):
                    self.instrument = pairs[choix]
                    #print(f"\n\033[92mVous avez sélectionné : {self.paire_selectionnee}\033[0m")
                    break
                else:
                    print("\033[91mNuméro invalide, veuillez réessayer.\033[0m")
            except ValueError:
                print("\033[91mEntrée invalide, veuillez entrer un numéro.\033[0m")

    def mis_a_jour_des_actifs(self):
        self.api.update_ACTIVES_OPCODE()
        actifs = self.api.get_all_ACTIVES_OPCODE()
        actifs_dict = {}

        for actif_info, actif_id in actifs.items():
            #print(f"{actif_info}: {actif_id},")
            actifs_dict[actif_info] = actif_id

        with open("constants.py", "w") as fichier:
            fichier.write("ACTIVES = {\n")
            for actif_nom, actif_id in actifs_dict.items():
                fichier.write(f'\t"{actif_nom}": {actif_id},\n')
            fichier.write("}\n")

        self.remplacer_constants()
        #print(f"\nTotal des paires disponibles : {len(actifs_dict)}")

    def remplacer_constants(self):
        chemin_iqoptionapi = os.path.join('iqoptionapi/constants.py')
        chemin_iqoptionapi_ = os.path.join(os.path.dirname(iqoptionapi.__file__), 'constants.py')
        chemin_iqoptionapi_ = chemin_iqoptionapi_.replace("\\", "/")
        print(f"chemin_iqoptionapi_ : {chemin_iqoptionapi_}")
        nouveau_fichier = 'constants.py'
        shutil.copyfile(nouveau_fichier, chemin_iqoptionapi)
        #print("Le fichier constants.py a été remplacé avec succès.")

    def is_market_open(self, instrument):
        try:
            # Obtenez l'état d'ouverture pour tous les marchés
            open_time = self.api.get_all_open_time()

            # Vérifiez si l'instrument est présent dans la liste
            if instrument in open_time:
                is_open = open_time[instrument]['open']
                return is_open
            else:
                print(f"Instrument {instrument} non trouvé dans les marchés disponibles.")
                return False
        except Exception as e:
            print(f"Erreur lors de la vérification de l'état du marché : {e}")
            return False

    @reconnect_on_failure
    def get_market_data_5min(self):
        #print(f"get data 5 ... ===  self.instrument : {self.instrument}")
        try:
            candles = self.api.get_candles(self.instrument, 300, 100, time.time())
            #print(f"Type de candles : {type(candles)}")

            if not candles:
                print("La condition not candles est remplie.")
                raise ValueError("Aucune donnée reçue pour les bougies.")

            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s')
            df.set_index('time', inplace=True)
            #df = df.iloc[:-1]
            return df
        except ValueError as ve:
            print(f"Erreur liée aux données ou au marché : {ve}")
            #wsqself.switch_to_next_instrument()  # Passer au marché suivant
            livre = random.choice(self.pairs_for_trade)
            self.instrument = livre[0]
        except Exception as e:
            print(f"Erreur lors de la récupération des données de marché: {e}")
            return pd.DataFrame()

    @reconnect_on_failure
    def get_market_data_2min(self):
        #print(f"get data 2 ...")
        try:
            candles = self.api.get_candles(self.instrument, 120, 100, time.time())
            if not candles:
                raise ValueError("Aucune donnée reçue pour les bougies.")
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s')
            df.set_index('time', inplace=True)
            df = df.iloc[:-1]
            return df
        except ValueError as ve:
            print(f"Erreur liée aux données ou au marché : {ve}")
            #wsqself.switch_to_next_instrument()  # Passer au marché suivant
            livre = random.choice(self.pairs_for_trade)
            self.instrument = livre[0]
            time.sleep(1)
        except Exception as e:
            print(f"Erreur lors de la récupération des données de marché: {e}")
            return pd.DataFrame()

    @reconnect_on_failure
    def get_market_data_1min(self):
        #print(f"get data 1 ...")

        try:
            candles = self.api.get_candles(self.instrument, 60, 100, time.time())
            #print(f"instrument : {self.instrument}")
            if not candles:
                raise ValueError("Aucune donnée reçue pour les bougies.")
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['from'], unit='s')
            df.set_index('time', inplace=True)
            #df = df.iloc[:-1]
            return df
        except ValueError as ve:
            print(f"Erreur liée aux données ou au marché : {ve}")
            #wsqself.switch_to_next_instrument()  # Passer au marché suivant
            livre = random.choice(self.pairs_for_trade)
            self.instrument = livre[0]
        except Exception as e:
            print(f"Erreur lors de la récupération des données de marché: {e}")
            return pd.DataFrame()

    def calculate_indicators(self, df):
        """ Calcule les indicateurs techniques nécessaires pour la stratégie """
        # Vérification si le DataFrame est valide
        if df is None or df.empty:
            print("Erreur : df est vide ou None.")
            return None

        #print(df.tail(5))

        required_columns = {'open', 'high', 'low', 'close'}
        if not required_columns.issubset(df.columns):
            print(f"Erreur : Colonnes manquantes {required_columns - set(df.columns)}")
            return None

        df['close'] = df['close'].astype(float)
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        df['SMA_5'] = ta.sma(df['close'], length=5)
        df['SMA_10'] = ta.sma(df['close'], length=10)
        df['SMA_15'] = ta.sma(df['close'], length=15)

        #df['RSI_20'] = ta.rsi(df['close'], length=20)

        df['RSI_20'] = ta_ta.momentum.RSIIndicator(close=df['close'], window=20).rsi()
        df['CCI'] = ta_ta.trend.CCIIndicator(high=df['high'], low=df['low'], close=df['close'], window=20).cci()

        df['DeMarker'] = self.de_marker(df)


        return df.dropna()

    def get_open_digital_markets(self):
        open_times = self.api.get_all_open_time()
        open_binary_markets = []

        if 'binary' in open_times:  # Remplacez 'digital' par 'binary'
            for pair, info in open_times['binary'].items():
                is_open = info.get('open', False)
                # Debugging pour voir les détails des paires
                # print(f"Paire : {pair}, Ouvert : {is_open}, Infos : {info}")

                if is_open and "NZ" not in pair and ":N" not in pair and "TRUMP" not in pair and pair in ACTIVES:  # Filtrage des paires spécifiques
                    open_binary_markets.append(pair)
                    self.paires_list.append(pair)

        if not open_binary_markets:
            print("Aucun marché binaire ouvert.")  # Message si aucun marché binaire n'est ouvert

        return open_binary_markets

    def get_open_digital_markets_digital(self):
        open_times = self.api.get_all_open_time()
        open_digital_markets = []

        if 'digital' in open_times:
            for pair, info in open_times['digital'].items():
                is_open = info.get('open', False)
                #print(f"Paire : {pair}, Ouvert : {is_open}, Infos : {info}")  # Debugging

                if is_open and "NZ" not in pair and ":N" not in pair and "TRUMP" not in pair and pair in ACTIVES:
                    open_digital_markets.append(pair)
                    self.paires_list.append(pair)

        if not open_digital_markets:
            print("Aucun marché digital ouvert.")  # Message pour indiquer que la liste est vide

        return open_digital_markets

    def calculate_expiration(self, minutes):
        """Calcule l'heure exacte d'expiration en fonction de la bougie actuelle."""
        now = datetime.now()
        next_expiration = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        return int((next_expiration - now).total_seconds() / 60)  # Retourne en minutes

    def execute_trade(self, action):
        """Exécute la transaction avec une expiration synchronisée."""
        expiration_minutes = self.calculate_expiration(10)  # Expiration dans 10 minutes
        self.back_into_signal = action

        if action == 'BUY':
            status, id = self.api.buy(self.mises[self.losses], self.instrument, "call", 1)
            #status, id = self.api.BUY_digital_spot_v2(self.instrument, self.mises[self.losses], "call", 1)
        elif action == 'SELL':
            status, id = self.api.buy(self.mises[self.losses], self.instrument, "put", 1)
            #status, id = self.api.BUY_digital_spot_v2(self.instrument, self.mises[self.losses], "put", 1)
        else:
            return None, None

        return status, id

    def trading_simulation(self, action):
        current_time = datetime.now()
        next_trade_time = (current_time + timedelta(minutes=(10 - current_time.minute % 10))).replace(second=0,
                                                                                                      microsecond=0)

        print(f"\033[92mEN MODE SIMULATION\033[0m , Ps : {self.losses}. En attente de la fin du bougie en cours....",
              end='\r')
        while True:
            time_remaining = (next_trade_time - datetime.now()).total_seconds()
            if time_remaining <= 0:
                break
            time.sleep(0.2)

        df = self.get_market_data()
        # Vérification de la taille de df avant le calcul des indicateurs
        if len(df) < 3:
            print("Pas assez de données")
            return 'hold'

        # Calcul des indicateurs avec suppression des valeurs NaN
        df = self.calculate_indicators(df)
        open = df['open'].iloc[-1]
        close = df['close'].iloc[-1]
        if (action == "BUY" and open < close) or (action == "sell" and close < open):
            self.in_simu = False

        return self.in_simu

    def calculate_next_minute(self):
        """ Calcule l'heure du prochain trade """
        current_time = datetime.now()
        next_trade_time = (current_time + timedelta(minutes=(1 - current_time.minute % 1))).replace(second=0,
                                                                                                    microsecond=0)
        return next_trade_time

    def calculate_next_minute_5(self):
        """ Calcule l'heure du prochain trade """
        current_time = datetime.now()
        next_trade_time = (current_time + timedelta(minutes=(5 - current_time.minute % 5))).replace(second=0,
                                                                                                    microsecond=0)
        return next_trade_time

    def display_countdown(self, next_trade_time):
        """ Affiche le compte à rebours jusqu'au prochain trade """
        #print(f"ccountdown !!!")
        #self.instrument = None
        while True:
            time_remaining = (next_trade_time - datetime.now()).total_seconds()

            if time_remaining <= 0:
                break

            prft = round((self.solde_act_ - self.solde_init_),2)
            prft_ = f"\033[91m{prft}\033[0m" if prft < 0 else f"\033[92m{prft}\033[0m"
            countdown = str(timedelta(seconds=int(time_remaining)))
            if self.point == 0:
                self.point += 1
                print("\r\033[K", end='', flush=True)
                print(f"\033[92mPROFIT_TOTAL\033[0m[{prft_}]  ==> Attente d'une position favorable\033[94m\033[0m    : \033[92m{countdown}\033[0m", end='', flush=True)
            elif self.point == 1:
                self.point += 1
                print("\r\033[K", end='', flush=True)
                print(f"\033[92mPROFIT_TOTAL\033[0m[{prft_}]  ==> Attente d'une position favorable\033[94m.\033[0m   : \033[92m{countdown}\033[0m", end='', flush=True)
            elif self.point == 2:
                self.point += 1
                print("\r\033[K", end='', flush=True)
                print(f"\033[92mPROFIT_TOTAL\033[0m[{prft_}]  ==> Attente d'une position favorable\033[94m..\033[0m  : \033[92m{countdown}\033[0m", end='', flush=True)
            elif self.point == 3:
                self.point = 0
                print("\r\033[K", end='', flush=True)
                print(f"\033[92mPROFIT_TOTAL\033[0m[{prft_}]  ==> Attente d'une position favorable\033[94m...\033[0m : \033[92m{countdown}\033[0m", end='', flush=True)


            time.sleep(1)

        print("\r\033[K", end='', flush=True)

    def start_trading(self):
        """ Démarre le trading automatique """
        if not self.connect_to_iq_option():
            return

        # if not self.select_preferred_market():
        #     return

        while True:
            # Nettoyer l'écran
            print("\033[2J\033[H", end="")
            if platform.system() == 'Windows':
                os.system('cls')
            else:
                os.system('clear')
            print("\033[33m")  # Début de la couleur verte


            print(f"\n_______________________________ VOTRE INFOS _____________________________________")
            print(f"1 - email          : \033[95m{self.email}\033[0m")
            print(f"2 - mot de passe   : \033[95m{self.password}\033[0m")
            print(f"3 - type de compte : \033[95m{self.account_type}\033[0m")
            print(f"4 - acif choisi    : \033[95m{self.instrument}\033[0m")
            print(f"5 - stop loss      : \033[95m{self.stop_loss}\033[0m")
            print(f"__________________________________________________________________________________")
            continuite = input("\033[0m(valider/arrêter/modifier) ? : \033[95m")

            if continuite == "valider":
                print("\033[92m✅ Paramètres validés !\033[0m")
                break

            elif continuite == "arrêter":
                print("\033[94m🔴 Le robot s'arrête dans 5s...\033[0m")
                time.sleep(5)
                exit()
            elif continuite == "modifier":
                try:
                    nbr_m = int(input("\033[0mEntrer le numéro du paramètre à modifier : \033[95m"))

                    if nbr_m == 3:
                        self.account_type = input("\033[0mType de compte (demo/real) : \033[95m").strip().lower()
                        if bot.account_type == "real":
                            self.api.change_balance("REAL")
                        else:
                            self.api.change_balance("PRACTICE")

                    elif nbr_m == 4:
                        pairs_ = self.get_open_digital_markets()
                        if pairs_:
                            self.choose_pair_to_trade(pairs_)
                        else:
                            print("\033[91m⚠️ Aucune paire disponible pour trader.\033[0m")

                    elif nbr_m == 5:
                        self.stop_loss = int(input("\033[0mStop loss : \033[95m"))

                    else:
                        self.email = input("\033[0mEmail : \033[95m")
                        self.password = input("\033[0mPassword : \033[95m")
                        self.connect_to_iq_option(1)


                except ValueError:
                    print("\033[91m⚠️ Entrée invalide, veuillez entrer un numéro valide.\033[0m")


        # Nettoyer l'écran
        print("\033[2J\033[H", end="")
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

        print("")
        label_width = 14
        value_width = 40
        total_width = label_width + value_width + 5
        top_border    = "╔" + "═" * total_width + "╗"
        bottom_border = "╚" + "═" * total_width + "╝"
        separator     = "║" + "═" * total_width + "║"
        col = "\033[91m" if self.account_type == "demo" else "\033[92m"
        print(f"\t\t\033[0m{top_border}")
        print(f"\t\t║ {'email'.ljust(label_width)} : \033[92m{self.email.ljust(value_width)}\033[0m ║")
        print(f"\t\t║ {'password'.ljust(label_width)} : {'*' * len(self.password):<{value_width}} ║")
        print(f"\t\t{separator}")
        print(f"\t\t║ {'type de compte'.ljust(label_width)} :{col} {self.account_type.ljust(value_width)}\033[0m ║")
        print(f"\t\t║ {'stop_loss'.ljust(label_width)} : \033[91m{str(self.stop_loss).ljust(value_width)}\033[0m ║")
        print(f"\t\t║ {'actif'.ljust(label_width)} : \033[93m{self.instrument.ljust(value_width)}\033[0m ║")
        print(f"\t\t║ {'payout'.ljust(label_width)} : \033[94m{"00"}\033[0m ║")
        print(f"\t\t║ {'solde_init'.ljust(label_width)} : \033[92m{str(self.solde_init_).ljust(value_width)}\033[0m ║")
        print(f"\t\t{bottom_border}\033[0m")
        print("")

        print(f"\t\tGREEN OPTION TRADING LANCEE AU DEMARRAGE SUR \033[92m{self.instrument}\033[0m.....")
        print("")

        # next_trade_time = self.calculate_next_minute()
        # self.display_countdown(next_trade_time)


        while self.in_trade:
            if not self.conn:
                self.ensure_connection(1)
            if self.losses == 0:
                next_trade_time = self.calculate_next_minute()
                self.display_countdown(next_trade_time)

            if self.last_signal is not None:
                status, id = self.execute_trade(self.last_signal)
                if status:
                    date_ouverture = datetime.now()
                    date_fermeture = (date_ouverture + timedelta(minutes=1)).replace(second=0, microsecond=0)

                    self.date_open = date_ouverture.strftime('%Y-%m-%d %H:%M:%S')
                    self.date_close = date_fermeture.strftime('%Y-%m-%d %H:%M:%S')

                    self.conn = False
                    position = "\033[92mAchat\033[0m" if self.last_signal == 'BUY' else "\033[33mVente\033[0m"
                    print(
                        f"\033[92mTrade placé avec succès\033[0m, Mise : \033[33m{self.amount:.2f}$\033[0m, Décision : {position} : \033[92mBONNE CHANCE...\033[0m",
                        end="\r")
                    self.check_trade_result(id, self.last_signal)

    @reconnect_on_failure
    def check_trade_result(self, id, signal):
        if not self.conn:
            self.ensure_connection(1)

        while True:
            try:
                profit = self.api.check_win_v3(id)
                #profit = self.api.check_win_digital_v2(id)
                if profit is not None:
                    break
            except Exception as e:
                self.handle_reconnection()

            time.sleep(0.2)

        position = "\033[92mAchat\033[0m" if signal == 'BUY' else "\033[33mVente\033[0m"
        mise_affiche = f"\033[96m{self.mises[self.losses]:.2f} $\033[0m" if self.mises[
                                                                                self.losses] > 10 else f" \033[96m{self.mises[self.losses]:.2f} $\033[0m"

        if profit > 0:
            self.total_profit += profit
            self.total_perte = 0
            self.payout = profit / self.mises[self.losses]
            profit_affiche = f" {self.total_profit:.2f} $" if self.total_profit > 0 else f"{self.total_profit:.2f} $"
            losse_affiche = f"\033[91m{self.losses}\033[95m" if self.losses != 0 else f"\033[92m{self.losses}\033[95m"
            print(
                f"|  \033[94m{self.date_open}\033[0m  |  \033[95m{self.date_close}\033[0m  |  {position}  |  Ps : {losse_affiche}  \033[0m|  Mise : {mise_affiche}  |   \033[92mgagné\033[0m   |   Profit : \033[94m{profit_affiche}\033[0m | {self.instrument}")
            self.losses = 0
            self.is_loss = False
            self.nb_recup = 0
            self.nb_trade_losses = 0
            self.is_renverse = False
            self.in_simu = False
            self.current_color = None
            self.demarrage = False
            self.search_signal = False
            self.back_into = True

            if self.total_profit >= self.profit_attendu:
                print("\033[92mFELICITATION, PROFIT ATTEINT :) !!!\033[0m")
                self.in_trade = False

        elif profit < 0:
            #print(f"total_perte : {self.total_perte}")
            self.total_profit -= self.amount
            self.total_perte -= self.amount

            self.nb_trade_losses += 1
            self.is_loss = False
            self.nb_recup += 1
            self.croisement = None
            self.demarrage = True
            self.search_signal = True
            self.back_into = False

            self.nb_recup = 0
            self.nb_trade_losses = 0


            self.payout = profit / self.mises[self.losses]
            profit_affiche = f" {self.total_perte:.2f} $" if self.total_perte < 0 else f"{self.total_perte:.2f} $"
            losse_affiche = f"\033[91m{self.losses}\033[95m" if self.losses != 0 else f"\033[92m{self.losses}\033[95m"
            print(
                f"|  \033[94m{self.date_open}\033[0m  |  \033[95m{self.date_close}\033[0m  |  {position}  |  Ps : {losse_affiche}  \033[0m|  Mise : {mise_affiche}  |   \033[91mperdu\033[0m   |   Pèrte  : \033[91m{profit_affiche}\033[0m | {self.instrument}")

            self.losses += 1

            if self.stop_loss < abs(int(self.total_perte)):
                print(f"\033[91mPERTE JUSQUE {self.total_perte} > {self.stop_loss} , donc arrêt du robot! \033[95m")
                self.in_trade = False

            if self.losses == self.max_losses:
                print("ARRET EN CAS DE PERTES SUCCESSIVES MAXIMAL ATTEINT :( !")
                self.in_trade = False

        #print(f"checked result!!!")

        self.amount = self.mises[self.losses]
        self.solde_act_ = self.api.get_balance()

    def handle_reconnection(self):
        """ Connexion à l'API IQ Option """
        self.api = IQ_Option(self.email, self.password)
        self.api.connect()
        if not self.api.check_connect():
            print("Echèc de réconnexion, prochain tentative dans 15s", end="\r")
        self.api.change_balance("PRACTICE")  # Utilisation du compte démo

if __name__ == "__main__":
    init()
    #email = input("Email : \033[92m")
    #password = input("\033[0mPassword : \033[95m")
    email = "tombokael4@gmail.com"
    password = "tombokael04"
    #account_type = input("\033[0mType de compte (demo/real) : \033[95m")
    #direcion = input("\033[0mDirection (BUY/SELL) : \033[95m")
    account_type = "demo"
    direcion = "BUY"

    profit = 1000
    mise_type = "normal"
    #account_type = "demo"
    max_losses = 1000

    #print("\033[0m")

    try:
        profit = float(profit)
        max_losses = int(max_losses)
    except:
        profit = 10
        max_losses = 10

    if max_losses == 0:
        max_losses = 10

    bot = TRADING(email, password, profit, mise_type, account_type, max_losses,direcion)
    bot.start_trading()

    # 5,5  ; 17,30  ;  42  ; 94,30   ;  104,65
