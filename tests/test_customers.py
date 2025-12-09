# /tests/test_customers.py

import unittest 
from app import create_app
from app.models import db, Customer
from app.utils.util import encode_token
from marshmallow import ValidationError

class TestCustomer(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customer(
                name='Test User', 
                email='test@example.com', 
                phone='123-456-7890', 
                password='123456')
            db.session.add(self.customer)
            db.session.commit()
            self.token = encode_token(self.customer.id, user_type='customer')
        
        
    # Customer Login (with token) Test - ⚡ Tested!
    def test_login_customer(self): 
        payload = {
            'email': 'test@example.com',
            'password': '123456'
        }
        response = self.client.post('/customers/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        
    # Negative Test - Wrong Password ⚡ Tested!   
        bad_payload = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        response_bad = self.client.post('/customers/login', json=bad_payload)
        self.assertEqual(response_bad.status_code, 401)
        self.assertIn('message', response_bad.json) 
    
    # Create a Customer Test - ⚡ Tested!
    def test_create_customer(self):
        payload = {
            "name": "Puka Roo",
            "email": "proo@gmail.com",
            "phone": "562-713-9089",
            "password": "123456"
        }
        
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], payload['name'])
    
    # Negative Test - Missing Phone Information ⚡ Tested! 
        payload = {
            "name": "Puka Roo",
            "email": "proo@gmail.com",
            "password": "123456"
        }
        
        response = self.client.post('/customers/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.json)
        
    # Get All Customers Test -⚡ Tested!   
    def test_get_customers(self):
        response = self.client.get('customers/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test User')
        
    # Negative Test - Invalid pagination parameters ⚡ Tested!
        bad_response = self.client.get('customers/?page=abc&per_page=xyz')
        self.assertEqual(bad_response.status_code, 200)
        self.assertEqual(len(bad_response.json), 1)
        self.assertEqual(bad_response.json[0]['name'], 'Test User')
        
    # Get a Specific Customer Test -⚡ Tested!
    def test_get_specific_customer(self):
        response = self.client.get('/customers/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test User')
        
    # Negative Test - Non-Existent Customer ID ⚡ Tested!
        response_bad = self.client.get('/customers/999')
        self.assertEqual(response_bad.status_code, 404)
        self.assertIn('error', response_bad.json)
    
    # Update a Specific Customer Test - ⚡ Tested!    
    def test_customer_update(self): 
        update_payload = {
            'name': 'Updated Customer',
            'email':'test@example.com',
            'phone':'123-456-7890',
            'password': '123456'
        }
        
        headers = {'Authorization':'Bearer ' + self.token}
        response = self.client.put('/customers/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], update_payload['name'])
        
    # Negative Test - Invalid Data ⚡ Tested!
        invalid_payload =  {'email': 'test@example.com', 'phone':'123-456-7890'}
        response_bad = self.client.put('/customers/', json=invalid_payload, headers=headers)
        self.assertEqual(response_bad.status_code, 400)
        self.assertIn('name', response_bad.json)
        
    # Delete a Specific Customer Test -⚡ Tested!
    def test_delete_customer(self):
        headers = {'Authorization': 'Bearer ' + self.token}
        customer_id = self.customer.id
        response = self.client.delete('/customers/', headers=headers)
        self.assertIsNotNone(response.json)
        self.assertEqual(
        response.json['message'],
        f'Customer id: {customer_id}, successfully deleted.'
        )
        self.assertEqual(response.status_code, 200)
        
    # Negative Test - Already Deleted Customer ⚡ Tested!
        response_bad = self.client.delete('/customers/', headers=headers)
        self.assertEqual(response_bad.status_code, 404)
        self.assertIn('error', response_bad.json)
    
    # Search for a Customer Based on Email Test - ⚡ Tested!
    def test_search_customer_by_email(self):
        email_to_search = self.customer.email
        response = self.client.get(f'/customers/search?email={email_to_search}')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreaterEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['email'], email_to_search)
        
    # Negative Test - No matching email ⚡ Tested!
        response_bad = self.client.get('/customers/search?email=nomatch@example.com')
        self.assertEqual(response_bad.status_code, 200)
        self.assertEqual(response_bad.json, [])
        
    
            