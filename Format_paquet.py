from enum import Enum

class Format_paquet(Enum) :

    #---Paquet d'établissement de connexion---
    #  --------------
    #  |Numero de con | B
    #  |Type de paquet| B
    #  |Adresse src   | B
    #  |Adresse dest  | B
    #   --------------
    #  8    32bits    1
    # Type paquet = 00001011(11)
    # Type paquet = 00001111(15)
    N_CONNECT = '!BBBB'

    #---refus de connexion et libération de connexion---
    #   --------------
    #  |Numero de con | B
    #  |Type de paquet| B
    #  |Adresse src   | B
    #  |Adresse dest  | B
    #  |Raison        | B
    #   --------------
    #  8    40 bits    1
    #Raison = Distant refuse la connexion(00000001 (1) )
    #       = Le fournisseur de service refuse (00000010 (2) )
    N_DISCONNECT_IND = '!BBBBB'

    #---Paquet transfert de données---
    #   --------------         Type de paquet =
    #  |Numero de con | B       -------------------
    #  |Type de paquet| B      | p(r)| M | P(s)| 0 |
    #  |Donnees       | 128B    -------------------
    #   --------------         8                   1
    #  16bits + 128bytes = 1040 bits
    NUMERO_CON = '!B'
    TYPE_PAQUET = '!B'
    # ****To pack a N_DATA_REQ see service_manipulation_donnee.pack_n_data_req***

    #---Paquet d'acquittement---
    #   ---------------
    #  |Numero de con  |
    #  |p(r)|0|0|0|0|1 |
    #   ---------------
    #  8    16bits     1
    N_AKN_POS = '!BB'
    #   ---------------
    #  |Numero de con  |
    #  |p(r)|0|1|0|0|1 |
    #   ---------------
    #  8    16bits     1
    N_AKN_NEG = '!BB'



'''
EXEMPLE D'UTILISATION DE LA LIBRAIRIE STRUCT
import struct

Packing data into bytes struct.pack(format, v1, v2, ...)
For packing N_CONNECT_REQ  
raw_data = struct.pack(N_CONNECT_REQ.value, 1, 15, 3, 4)
raw_data = '\x01\x0f\x03\x04' Is of the type bytes(1 bytes = 8 bits) with a length of 4(bytes).

Unpacking data into a tuple struct.unpack(format, raw_data)
For unpacking N_CONNECT_REQ
data = struct.unpack(N_CONNECTE_REQ.value, raw_data)
data = (1,15,3,4) Is a tuple
'''
