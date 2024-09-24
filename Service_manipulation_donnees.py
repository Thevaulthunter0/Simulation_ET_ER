import struct 
import Format_paquet as FP

class service_manipulation_donnees() :
    '''
    Définition : Pack une primitive N_DATA_REQ
    Because N_DATA_REQ is a complexe structure(a struct insine of a struct)
    We need to create it by combining multiples structure.
    Input :
        _numCon need to be a 8 bits integer
        _numPaquet need to be 3 bits integer
        _dernierPaquet need to be 1 bit integer
        _numProchainPaquet need to be 3 bits integer
        _donnee need to be smaller or equal to 128 Bytes and of type bytes
    Output :
        bytes to be unpack
    '''
    def pack_n_data_req(_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, _donnee) :
        #Creer la structure Numero de con
        numCon = struct.pack(FP.Format_paquet.NUMERO_CON.value, _numCon)
        #Creer la structure TYPE_PAQUET 
        type_paquet = (_numPaquet << 5) | (_dernierPaquet << 4) | ( _numProchainPaquet<< 1)
        type_paquet_pack = struct.pack(FP.Format_paquet.TYPE_PAQUET.value, type_paquet)
        #Creer la structure Data
        if len(_donnee) < 128 :
            donnee = donnee.lJust(128, b'\x00')
        
        return numCon + type_paquet_pack + _donnee 
    
    '''
    Définition : Unpack une primitive N_DATA_REQ
    Input :
        pack_data bytes 
    Output : 
        tuple (_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee)
    '''
    def unpack_n_data_req(pack_data) :
        _numCon = pack_data[0]
        type_paquet = pack_data[1]
        _numPaquet = ((type_paquet >> 5) & 0b111)
        _dernierPaquet = ((type_paquet >> 4) & 0b1)
        _numProchainPaquet = ((type_paquet) & 0b111)
        longeur_donnee = len(pack_data)
        donnee = pack_data[2:2 + longeur_donnee]
        return (_numCon, _numPaquet, _dernierPaquet, _numProchainPaquet, donnee)

    '''
    Définition : Pack une primitive de type N_CONNECT
    Input :
        _numCon 8 bits integer
        _typePaquet 8 bits integer
        _AddrSrc 8 bits integer
        _AddrDest 8 bits integer
    Output :
        bytes to be unpack
    '''
    def pack_n_connect(_numCon, _typePaquet, _AddrSrc, _AddrDest) :
        return struct.pack(FP.Format_paquet.N_CONNECT, _numCon, _typePaquet,
            _AddrSrc, _AddrDest)
    '''
    Définition : Unpack une primitive de type N_CONNECT
    Input : 
        pack_data bytes
    Output :
        tuple (_numCon, _typePaquet, _AddrSrc, _AddrDest)
    '''
    def unpack_n_connect(pack_data) :
        return struct.unpack(FP.Format_paquet.N_CONNECT, pack_data)
    '''
    Définition : pack une primitive de type N_DISCONNECT_IND
    Input :
        _numCon 8 bits integer
        _typePaquet 8 bits integer
        _AddrSrc 8 bits integer
        _AddrDest 8 bits integer
        _Raison 8 bits integer
    Output :
        bytes to be unpack
    '''
    def pack_n_disconnect_ind(_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison) :
        return struct.pack(FP.Format_paquet.N_DISCONNECT_IND, _numCon, _typePaquet,
            _AddrSrc, _AddrDest, _Raison)
    '''
    Définition : Unpack une primitive de type N_DISCONNECT_IND
    Input :
        pack_data bytes
    Output :
        tuple (_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison)
    '''
    def unpack_n_disconnect_ind(pack_data) :
        return struct.unpack(FP.Format_paquet.N_DISCONNECT_IND, pack_data)
    '''
    Définition : pack une primitive de type N_AKN_POS
    Input : 
        _numCon 8 bits integer
        _numProchainPaquet 3 bits integer
    Output :
        bytes to be unpack
    '''
    def pack_n_akn_pos(_numCon, _numProchainPaquet) :
        numCon = struct.pack(FP.Format_paquet.NUMERO_CON.value, _numCon)
        dernierByte = ((_numProchainPaquet >> 5) & 0b111) << 5 | 0b00001
        return numCon + dernierByte
    
    '''
    Défintion : Unpack une primitive de type N_AKN_POS
    Input : 
        pack_data bytes
    Output : 
        tuple(_numCon, _numPorchainPaquet)
    '''
    def unpack_n_akn_pos(pack_data) :
        _numCon = pack_data[0]
        _dernierByte = pack_data[1]
        _numProchainPaquet = _dernierByte[8:5]
        return (_numCon, _numProchainPaquet)
    '''
    Définition : Pack une primitive de type N_AKN_NEG
    Input : 
        _numCon 8 bits integer
        _numProchainPaquet 3 bits integer
    Output :
        Bytes to be unpack
    '''
    def pack_n_akn_neg(_numcon, _numProchainPaquet) :
        numCon = struct.pack(FP.Format_paquet.NUMERO_CON.value, _numcon)
        dernierByte = ((_numProchainPaquet >> 5) & 0b111) << 5 |0b01001
        return numCon + dernierByte
    '''
    Définition : Unpack une primitive de type N_AKN_NEG
    Input :
        pack_data byes
    Output :
        Tuple(_numCon,_numProchainPaquet)

    '''
    def unpack_n_akn_neg(pack_data) :
        _numCon = pack_data[0]
        _dernierByte = pack_data[1]
        _numProchainPaquet = _dernierByte[8:5]
        return (_numCon, _numProchainPaquet)