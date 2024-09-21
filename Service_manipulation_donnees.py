import struct 
import Format_paquet as FP

class service_manipulation_donnees() :
    '''
    Because N_DATA_REQ is a complexe structure(a struct insine of a struct)
    We need to create it by combining multiples structure.
    _numCon need to be a 8 bits integer
    _numPaquet need to be 3 bits integer
    _dernierPaquet need to be 1 bit integer
    _numProchainPaquet need to be 3 bits integer
    data need to be smaller or equal to 128 Bytes and of type bytes
    '''
    def pack_n_data_req(_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee) :
        #Creer la structure Numero de con
        numCon = struct.pack(FP.Format_paquet.NUMERO_CON.value, _numCon)
        #Creer la structure TYPE_PAQUET 
        type_paquet = (_numPaquet << 5) | (_dernierPaquet << 4) | ( _numProchainPaquet<< 1)
        type_paquet_pack = struct.pack(FP.Format_paquet.TYPE_PAQUET.value, type_paquet)
        #Creer la structure Data
        if len(donnee) < 128 :
            donnee = donnee.lJust(128, b'\x00')
        
        return numCon + type_paquet_pack + donnee 
    
    def unpack_n_data_req(pack_data, longeur_donnee) :
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = (type_paquet >> 5) & 0b111
        _dernierPaquet = (type_paquet >> 4) & 0b1
        _numProchainPaquet = (type_paquet) & 0b111
        donnee = pack_data[2:2 + longeur_donnee]
        return (_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee)

    def pack_n_connect(_numCon, _typePaquet, _AddrSrc, _AddrDest) :
        return struct.pack(FP.Format_paquet.N_CONNECT, _numCon, _typePaquet,
            _AddrSrc, _AddrDest)

    def unpack_n_connect(data) :
        return struct.unpack(FP.Format_paquet.N_CONNECT, data)

    def pack_n_disconnect_ind(_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison) :
        return struct.pack(FP.Format_paquet.N_DISCONNECT_IND, _numCon, _typePaquet,
            _AddrSrc, _AddrDest, _Raison)
    
    def unpack_n_disconnect_ind(data) :
        return struct.unpack(FP.Format_paquet.N_DISCONNECT_IND, data)

#   def pack_n_akn_pos() :
#       pass
#   def unpack_n_akn_pos() :
#       pass
#   def pack_n_akn_neg() :
#       pass
#   def unpack_n_akn_neg() :
#       pass