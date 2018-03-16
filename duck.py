# -*- encoding: utf-8 -*-

import requests
from lxml.etree import HTML
from urllib.parse import urlparse, parse_qs, unquote
import uuid

from .config import Configuration

class DuckImageResult :

    def __init__(self, result) :
        self.data = dict()
        for key in ('title', 'width', 'height') :
            self.data[key] = result[key]
        self.data['url'] = unquote(result['url'])
        self.data['image'] = unquote(result['image'])
        self.data['thumbnail'] = unquote(result['thumbnail'])

    @property
    def uuid(self) :
        return uuid.uuid3(uuid.NAMESPACE_URL, self.data['image'])

    @property
    def url(self) :
        return self.data['url']
    
    @property
    def image(self) :
        return self.data['image']

    @property
    def thumbnail(self) :
        return self.data['thumbnail']

    @property
    def title(self) :
        return self.data['title']
    
    @property
    def width(self) :
        return self.data['width']

    @property
    def height(self) :
        return self.data['height']

class DuckImageSearch :

    def __init__(self) :
        self.config = Configuration()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent' : self.config.get('USER_AGENT')
        })
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
        
        params = dict()
        params['q'] = search
        params['t'] = 'ffsb'
        params['ia'] = 'images'
        params['iar'] = 'images'
        params['iax'] = 'images'

        page = self.session.get(
            'https://duckduckgo.com/',
            params=params
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

        self.params['o'] = 'json'
        self.params['p'] = -1
        for key in ('l', 'q', 'vqd') :
            self.params[key] = script_params[key]

        self.prepared = True

        
    def fetch(self, start=0) :

        if not self.prepared :
            return
        
        self.params['s'] = start

        jsi = self.session.get(
            'https://duckduckgo.com/i.js',
            params=self.params
        )

        for result in jsi.json()['results'] :
            r = DuckImageResult(result)
            self._results[r.uuid] = r

    def mfetch(self, start=0, num=100) :
        for lot in range(start, start + num, 50) :
            self.fetch(lot)
        
