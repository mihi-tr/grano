import unittest
import json
from copy import deepcopy

from grano.test.helpers import AUTHZ_HEADER

NETWORK_FIXTURE = {'slug': 'net', 'title': 'Test Network'}

ENTITY2_FIXTURE = {'title': 'Calvin', 
                  'type': 'person',
                  'network': 'net',
                  'birth_day': '2011-01-01',
                  'birth_place': 'The Tree',
                  'death_day': '2012-01-01',
                  'description': 'A school boy'}

ENTITY1_FIXTURE = {'title': 'Hobbes', 
                  'type': 'person',
                  'network': 'net',
                  'birth_day': '2011-01-01',
                  'birth_place': 'The Tree',
                  'death_day': '2012-01-01',
                  'description': 'A teddy bear'}

RELATION_FIXTURE = {'network': 'net', 'link_type': 'friendOf', 'type': 'social'}

from grano.core import db
from grano.model import Network, Schema
from grano.test.helpers import make_test_app, tear_down_test_app
from grano.test import helpers as h

class RelationAPITestCase(unittest.TestCase):

    def setUp(self):
        self.app = make_test_app()
        self.make_fixtures()

    def tearDown(self):
        tear_down_test_app()

    def make_fixtures(self):
        self.app.post('/api/1/networks',
                    headers=AUTHZ_HEADER,
                    data=NETWORK_FIXTURE)
        network = Network.by_slug(NETWORK_FIXTURE['slug'])
        Schema.create(network, Schema.RELATION,
                      h.TEST_RELATION_SCHEMA)
        Schema.create(network, Schema.ENTITY,
                      h.TEST_ENTITY_SCHEMA)
        res = self.app.post('/api/1/net/entities', 
                    headers=AUTHZ_HEADER,
                    data=ENTITY1_FIXTURE, 
                    follow_redirects=True)
        body = json.loads(res.data)
        self.source_id = body['id']
        res = self.app.post('/api/1/net/entities',
                    headers=AUTHZ_HEADER,
                    data=ENTITY2_FIXTURE, 
                    follow_redirects=True)
        body = json.loads(res.data)
        self.target_id = body['id']
        RELATION_FIXTURE['source'] = self.source_id
        RELATION_FIXTURE['target'] = self.target_id
        res = self.app.post('/api/1/net/relations', 
                    headers=AUTHZ_HEADER,
                    data=RELATION_FIXTURE, 
                    follow_redirects=True)
        print res.data
        body = json.loads(res.data)
        self.id = body['id']

    def test_network_index(self):
        res = self.app.get('/api/1/net/relations')
        body = json.loads(res.data)
        assert len(body)==1, body
    
    def test_get(self):
        res = self.app.get('/api/1/net/relations/%s' % self.id)
        body = json.loads(res.data)
        assert body['link_type']==RELATION_FIXTURE['link_type'], body
    
    def test_history(self):
        res = self.app.get('/api/1/net/relations/%s/history' % self.id)
        body = json.loads(res.data)
        assert len(body)==1, body

    def test_get_non_existent(self):
        res = self.app.get('/api/1/net/relations/bonobo')
        assert res.status_code==404,res.status_code

    def test_relation_create(self):
        data = deepcopy(RELATION_FIXTURE)
        data['link_type'] = 'toyOf'
        res = self.app.post('/api/1/net/relations', 
                      data=data,
                      headers=AUTHZ_HEADER,
                      follow_redirects=True)
        body = json.loads(res.data)
        assert body['link_type']==data['link_type'], body

    def test_relation_create_invalid(self):
        data = {'source': 'no', 'target': self.target_id}
        res = self.app.post('/api/1/net/relations', 
                      data=data,
                      headers=AUTHZ_HEADER,
                      follow_redirects=True)
        assert res.status_code==400,res.status_code

    def test_update(self):
        res = self.app.get('/api/1/net/relations/%s' % self.id)
        body = json.loads(res.data)
        body['link_type'] = 'foeOf'
        res = self.app.put('/api/1/net/relations/%s' % self.id, 
                      headers=AUTHZ_HEADER,
                      data=body)
        assert res.status_code==200,res.status_code
        body = json.loads(res.data)
        assert body['link_type']=='foeOf', body
        
        res = self.app.get('/api/1/net/relations/%s/history' % self.id)
        body = json.loads(res.data)
        assert len(body)==2, body

    def test_relation_delete_nonexistent(self):
        res = self.app.delete('/api/1/net/relations/the-one',
                        headers=AUTHZ_HEADER,)
        assert res.status_code==404,res.status_code

    def test_relation_delete(self):
        res = self.app.delete('/api/1/net/relations/%s' % self.id,
                        headers=AUTHZ_HEADER)
        assert res.status_code==410,res.status_code
        res = self.app.get('/api/1/net/relations/%s' % self.id)
        assert res.status_code==404,res.status_code




