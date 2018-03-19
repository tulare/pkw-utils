# -*- encoding: utf-8 -*-

from lxml.etree import HTML
from urllib.parse import urlparse, parse_qs, unquote, urljoin
from html import unescape
import uuid

class FetchError(Exception) :
    pass

class FetchDone(Exception) :
    pass

DUCK_IMAGE = {
    'image'     : ('image',     True,  (unquote,)),
    'title'     : ('title',     False, ()),
    'url'       : ('url',       False, (unquote,)),
    'width'     : ('width',     False, ()),
    'height'    : ('height',    False, ()),    
    'thumbnail' : ('thumbnail', False, (unquote,)),
}

DUCK_TEXT = {
    'url'       : ('u', True,  (unquote,)),    
    'site'      : ('i', False, ()),
    'title'     : ('t', False, (unescape,)),
    'text'      : ('a', False, (unescape,)),
    'provider'  : ('s', False, ()),
}

DUCK_FILTER = {
    'STRICT' : None,
    'MODERATE' : -1,
    'DISABLE' : -2
}

class DuckStore :

    def __init__(self, source, descriptor) :
        self.source = source
        self.data = {}
        for key, props in descriptor.items() :
            name, is_uuid, post_traits = props
            if is_uuid :
                self.key_uuid = key
            try :
                self.data[key] = self.source[name]
                for p in post_traits :
                    self.data[key] = p(self.data[key])
            except :
                self.data[key] = None

    def __getattr__(self, attr) :
        try :
            return self.data[attr]
        except KeyError :
            raise AttributeError

    @property
    def uuid(self) :
        return uuid.uuid3(uuid.NAMESPACE_URL, self.data[self.key_uuid])

class DuckSearch :

    def __init__(self, session, lang=None, pFilter=None) :
        self.session = session

        self.lang = lang or 'wt-wt'
        self.filter = str(pFilter) if pFilter else None
        self.cookies = {
            'p' : self.filter,
            'ah' : 'wt-wt',
            'l' : self.lang,
        }

        self.descriptor = DUCK_TEXT
        self.script = 'd.js'
        self.script_next = None

        self.reset()

    @property
    def results(self) :
        return list(self._results.values())

    @property
    def length(self) :
        return len(self._results)

    def reset(self) :
        self._results = dict()
        self.prepared = False

    def search(self, search) :
        self.params = dict()
        
        page = self.session.get(
            'https://duckduckgo.com/',
            params={
                'q' : search,
                't' : 'ffsb',
            },
            cookies=self.cookies
        )
        tree = HTML(page.content)
        script = tree.xpath('//script[contains(.,".js")]')[0]
            
        script_url = next(
            filter(
                lambda text : text.startswith("nrje"),
                script.text.split(';')
            )
        ).split("'")[1]

        script_params = parse_qs(urlparse(script_url).query)
        # print(script_params)

        for key in script_params :
            self.params[key] = script_params[key][0]

        self.params['o'] = 'json'

        self.prepared = True


    def fetch(self, start=0) :

        if not self.prepared :
            raise FetchError('search not prepared')

        self.script_next = None
        self.params['s'] = start
        self.params['p'] = -1 if self.filter else 1

        try :
            jsi = self.session.get(
                urljoin(
                    'https://duckduckgo.com',
                    self.script
                ),
                params=self.params,
                cookies=self.cookies
            )

            json = jsi.json()

            for result in json['results'] :
                if 'n' in result :
                    self.script_next = result['n']
                else :
                    r = DuckStore(result, self.descriptor)
                    self._results[r.uuid] = r

            if 'next' in json :
                self.script_next = json['next']
            
        except Exception as e :
            raise FetchError('{!r}'.format(e))

        return self.length

    def fetch_next(self) :

        if not self.prepared :
            raise FetchError('search not prepared')

        if self.script_next is None :
            raise FetchDone('no data to fetch')

        script_next = self.script_next

        try :
            self.script_next = None
            jsi = self.session.get(
                urljoin(
                    'https://duckduckgo.com',
                    script_next
                ),
                params={ 'vqd' : self.params['vqd'] },
                cookies=self.cookies                    
            )

            json = jsi.json()

            for result in json['results'] :
                if 'n' in result :
                    self.script_next = result['n']
                else :
                    r = DuckStore(result, self.descriptor)
                    self._results[r.uuid] = r

            if 'next' in json :
                self.script_next = json['next']

        except Exception as e :
            raise FetchDone('{!r}'.format(e))
            

        return self.length

    def fetch_all(self) :
        if not self.prepared :
            raise FetchError('search not prepared')

        self.fetch()
        while True :
            try :
                self.fetch_next()
            except FetchDone :
                break

        return self.length
    

class DuckImageSearch(DuckSearch) :

    def __init__(self, session, lang=None, pFilter=None) :
        super().__init__(session, lang, pFilter)
        self.script = 'i.js'
        self.descriptor = DUCK_IMAGE

        
