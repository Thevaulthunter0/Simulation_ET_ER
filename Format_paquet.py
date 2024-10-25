from enum import Enum

class Format_paquet(Enum):
    # --- Paquet d'établissement de connexion ---
    N_CONNECT = "!BBBB"

    # --- Refus de connexion et libération de connexion ---
    # --- Refus de connexion et libération de connexion ---
    N_DISCONNECT_IND = "!BBBBB"

    # --- Paquet de demande de liberation ---
    N_DISCONNECT_REQ = "!BBBB"

    # --- Paquet transfert de données ---
    NUMERO_CON = "!B"
    TYPE_PAQUET = "!B"

    # --- Paquet d'acquittement ---
    N_AKN_POS = "!BB"
    N_AKN_NEG = "!BB"