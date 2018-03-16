# -*- encoding: utf-8 -*-

import winreg

HKEYS = {
    item[0] : item[1]
    for item in filter(
        lambda it : it[0].startswith('HKEY_'),
        vars(winreg).items()
    )
}

KEYSAM = {
    item[0] : item[1]
    for item in filter(
        lambda it : it[0].startswith('KEY_'),
        vars(winreg).items()
    )
}

REGTYPES = {
    item[0] : item[1]
    for item in filter(
        lambda it : it[0].startswith('REG_'),
        vars(winreg).items()
    )
} 

class Registre :

    def __init__(self, hkey='HKEY_CURRENT_USER', path='') :
        self._hkey = hkey
        self._path = path
        self._root = winreg.ConnectRegistry(None, HKEYS[self._hkey])
        self._node = winreg.OpenKey(self._root, self._path)

    @property
    def hkey(self) :
        return self._hkey
    
    @property
    def path(self) :
        return self._path

    @property
    def abspath(self) :
        return '{}\\{}'.format(self._hkey, self._path)

    @property
    def root(self) :
        return self._root

    @property
    def node(self) :
        return self._node

    @property
    def values(self) :
        _values = {}
        indice = 0
        # valeur nommées
        while True :
            try :
                nodeVal = winreg.EnumValue(self._node, indice)
                _values[nodeVal[0]] = nodeVal[1]
                indice += 1
            except Exception as e :
                break

        return _values

    @property
    def keys(self) :
        _keys = []
        nbNodes, _, _ = winreg.QueryInfoKey(self._node)
        # return [ winreg.EnumKey(self._node, indice) for indice in range(nbNodes) ]
        for indice in range(nbNodes) :
            try :
                node_path = winreg.EnumKey(self._node, indice)
                _keys.append(node_path)
            except Exception as e :
                print('{}\\{} : {!r}'.format(self.path, node_path, e))

        return _keys

    @property
    def childKeys(self) :
        _nodes = {}
        nbNodes, _, _ = winreg.QueryInfoKey(self._node)
        for indice in range(nbNodes) :
            try :
                node_path = winreg.EnumKey(self._node, indice)
                new_path=self._path + '\\' + node_path if self._path else self._path + node_path
                _nodes[node_path] = Registre(
                    hkey=self._hkey,
                    path=new_path
                )
            except Exception as e :
                print('{}\\{} : {!r}'.format(self.path, node_path, e))
                
        return _nodes


    def getKey(self, path) :
        nbNodes, _, _ = winreg.QueryInfoKey(self._node)
        for indice in range(nbNodes) :
            try :
                node_path = winreg.EnumKey(self._node, indice)
                if node_path == path :

                    if self._path :
                        new_path = self._path + '\\' + node_path
                    else :
                        new_path = self._path + node_path
            
                    return Registre(
                        hkey=self._hkey,
                        path=new_path,
                    )
            except Exception as e :
                print('{}\\{} : {!r}'.format(self.path, node_path, e))

    def createKey(self, path) :
        winreg.CreateKey(self._node, path)

    def deleteKey(self, path, force=False) :
        if path in self.keys :
            # doit-on nettoyer les sous-clés d'abord ?
            if force :
                deletion_point = self.getKey(path)
                for subkeys in deletion_point.keys :
                    deletion_point.deleteKey(subkeys, force)
            # nettoie la clef, ne marche pas si elle contient des sous-clés
            winreg.DeleteKey(self._node, path)
        else :
            print('invalid key: \'{}\''.format(path))
      

    def getValue(self, name=None, default=None) :
        try :
            return self.values[name]
        except Exception as e :
            print('{!r}'.format(e))
            return default

    def setValue(self, name, value, reg_type='REG_SZ') :
        key = winreg.OpenKey(self._node, '', 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, name, 0, REGTYPES[reg_type], value)

    def deleteValue(self, name) :
        try :
            key = winreg.OpenKey(self.node, '', 0, winreg.KEY_WRITE)
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
        except Exception as e :
            print('{!r}'.format(e))

    def clearValues(self) :
        for val in self.values :
            self.deleteValue(val)

    def clear(self, force=False) :
        try :
            for key in self.keys :
                self.deleteKey(key, force=force)
            self.clearValues()
        except Exception as e :    
            print('clear: \'{}\' {!r}'.format(key, e))
            
