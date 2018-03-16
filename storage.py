# -*- encoding: utf-8 -*-

import os
import urllib.parse
import uuid

class Storage :

    def __init__(self, url, root, prefix=None, flat=False, add_uuid=False, mime=None) :
        self.url = url
        self.root = root
        parsed = urllib.parse.urlparse(self.url)

        # filename
        self.filename = os.path.basename(parsed.path)
        if prefix :
            self.filename = '{}-{}'.format(prefix, self.filename)
        if add_uuid :
            self.filename += '-{}'.format(uuid.uuid3(uuid.NAMESPACE_URL, self.url))
        if mime :
            self.filename += '.' + mime.split('/').pop()

        # path
        dirnames = os.path.dirname(parsed.path).split('/')[1:]
        category = ''
        if len(dirnames) > 1 :
            category = dirnames.pop(0) + '/'
        prefix = category + '_'.join(dirnames)
        if flat :
            self.path = '{}/'.format(
                self.root,
            )
        else :
            self.path = '{}/{}/{}/'.format(
                self.root,
                parsed.netloc.replace(':','_'),
                prefix,
            )

        # pathname
        self.pathname = self.path + self.filename

    def write(self, data) :
        os.makedirs(self.path, exist_ok=True)
        with open(self.pathname, 'wb') as fd :
            fd.write(data)
        
