# /tests/test_inventory.py

import unittest 
from app import create_app
from app.models import db, Inventory, Mechanic
from app.utils.util import encode_token
from marshmallow import ValidationError

class TestInventory(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.inventory = Inventory(
                part_name='Test Part', 
                price='29.99')
            self.mechanic = Mechanic(
                name='Test Mechanic',
                email='testmech@email.com',
                phone='123-456-7890',
                salary="50000",
                password='123456'
            )
            db.session.add(self.inventory)
            db.session.add(self.mechanic)
            db.session.commit()
            self.inventory_id = self.inventory.id
            self.inventory_name = self.inventory.part_name
            self.token = encode_token(self.mechanic.id, user_type='mechanic')
    
# Create an Inventory Item Test - ⚡ Tested!
    def test_create_inventory(self):
        payload = {
            "part_name": "Test Part 2",
            "price": "29.99"
        }  
        response = self.client.post('/inventory/', json=payload,  headers={"Authorization": f"Bearer {self.token}"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], payload['part_name'])
    
    # Negative Test - Missing Price Information ⚡ Tested! 
    def test_create_inventory_missing_price(self): 
        payload = {
            "part_name": "Test Part"
        }
        response = self.client.post('/inventory/', json=payload, headers={"Authorization": f"Bearer {self.token}"} )
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json)
        
    # Get All Inventory Test - ⚡ Tested!
    def test_get_inventory(self):
        response = self.client.get('/inventory/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['part_name'], 'Test Part')
        
    # Negative Test - Invalid pagination parameters ⚡ Tested!
    def test_invalid_get_inventory(self):
        bad_response = self.client.get('/inventory/?page=abc&per_page=xyz')
        self.assertEqual(bad_response.status_code, 200)
        self.assertEqual(len(bad_response.json), 1)
        self.assertEqual(bad_response.json[0]['part_name'], 'Test Part')
        
    # Get a Specific Inventory Item Test -⚡ Tested!
    def test_get_specific_inventory(self):
        response = self.client.get('/inventory/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['part_name'], 'Test Part')
        
    # Negative Test - Non-Existent Inventory Item ⚡ Tested!
    def test_invalid_get_specific_inventory(self):
        response_bad = self.client.get('/inventory/999')
        self.assertEqual(response_bad.status_code, 404)
        self.assertIn('error', response_bad.json)
    
    # Update a Specific Inventory Item Test - ⚡ Tested!
    def test_inventory_update(self): 
        update_payload = {
            'part_name': 'Updated Part',
            'price':'49.99',
        }
        headers={"Authorization": f"Bearer {self.token}"}
        response = self.client.put(f'/inventory/{self.inventory_id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['part_name'], update_payload['part_name'])
        
    # Negative Test - Invalid Data / Missing Part Name - ⚡ Tested!
    def test_invalid_inventory_update(self): 
        invalid_payload =  {'price': 'XXXXX'}
        headers={"Authorization": f"Bearer {self.token}"}
        response = self.client.put(f'/inventory/{self.inventory_id}', json=invalid_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('price', response.json)
        
    # Delete a Specific Inventory Item Test - ⚡ Tested!
    def test_delete_inventory(self):
        headers={"Authorization": f"Bearer {self.token}"}
        inventory_id = self.inventory.id
        response = self.client.delete(f'/inventory/{self.inventory_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
        response.json['message'],
        f'inventory id: {inventory_id}, successfully deleted.'
        )
        
    # Negative Test - Already Deleted Inventory Item - ⚡ Tested!
    def test_invalid_delete_inventory(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        self.client.delete(f'/inventory/{self.inventory_id}', headers=headers)
        response = self.client.delete(f'/inventory/{self.inventory_id}', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
    
    # Search for an Inventory Item Based on Email Test - ⚡ Tested!
    def test_search_inventory_by_part_name(self):
        response = self.client.get(f'/inventory/search?part_name={self.inventory_name}')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, dict)
        self.assertEqual(response.json['part_name'], self.inventory_name)
        
    # Negative Test - No matching part name ⚡ Tested!
    def test_search_invalid_inventory_by_part_name(self):
        response = self.client.get('/inventory/search?part_name=XXXX')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {})
        
    
            