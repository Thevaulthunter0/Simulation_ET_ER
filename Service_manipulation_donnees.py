import struct 
import Format_paquet as FP

class service_manipulation_donnees() :
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
        return struct.pack(FP.Format_paquet.N_CONNECT.value, _numCon, _typePaquet,
            _AddrSrc, _AddrDest)
    '''
    Définition : Unpack une primitive de type N_CONNECT
    Input : 
        pack_data bytes
    Output :
        tuple (_numCon, _typePaquet, _AddrSrc, _AddrDest)
    '''
    def unpack_n_connect(pack_data) :
        return struct.unpack(FP.Format_paquet.N_CONNECT.value, pack_data)
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
        return struct.pack(FP.Format_paquet.N_DISCONNECT_IND.value, _numCon, _typePaquet,
            _AddrSrc, _AddrDest, _Raison)
    '''
    Définition : Unpack une primitive de type N_DISCONNECT_IND
    Input :
        pack_data bytes
    Output :
        tuple (_numCon, _typePaquet, _AddrSrc, _AddrDest, _Raison)
    '''
    def unpack_n_disconnect_ind(pack_data) :
        return struct.unpack(FP.Format_paquet.N_DISCONNECT_IND.value, pack_data)
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

#   def pack_n_akn_pos() :
#       pass
#   def unpack_n_akn_pos() :
#       pass
#   def pack_n_akn_neg() :
#       pass
#   def unpack_n_akn_neg() :
#       pass
    '''
    def unpack_n_akn_neg(pack_data) :
        _numCon = pack_data[0]
        _dernierByte = pack_data[1]
        _numProchainPaquet = _dernierByte[8:5]
        return (_numCon, _numProchainPaquet)
    
    def unpack_N_DATA_req(data):
        _numCon = struct.unpack('B', data[0:1])[0]  # Extraire le premier octet
        _data = data[1:]  # Récupérer le reste des données après le premier octet

        return _numCon, _data

    def pack_N_DATA_req(_numCon, _data):
        if isinstance(_data, str):
            _data = _data.encode()  # Convertir la chaîne en bytes

        # On empaquette un octet pour le numéro de connexion suivi du paquet de données
        return struct.pack('B', _numCon) + _data
    
        # Paquet de communication etablie
    @staticmethod
    def pack_comm_etablie(_numCon, _AddrSrc, _AddrDest):
        return struct.pack(
            FP.Format_paquet.N_CONNECT.value, _numCon, 15, _AddrSrc, _AddrDest     #'00001111' = 15
        )

    @staticmethod
    def unpack_comm_etablie(data):
        return struct.unpack(FP.Format_paquet.N_CONNECT.value, data)
    
    @staticmethod
    def pack_n_disconnect_req(_numCon, _typePaquet, _AddrSrc, _AddrDest):
        return struct.pack(
            FP.Format_paquet.N_DISCONNECT_IND.value,
            _numCon,
            _typePaquet,
            _AddrSrc,
            _AddrDest,
        )

    @staticmethod
    def unpack_n_disconnect_req(data):
        return struct.unpack(FP.Format_paquet.N_DISCONNECT_IND.value, data)