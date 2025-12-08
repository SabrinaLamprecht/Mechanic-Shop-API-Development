# /tests/test_mechanics.py

import unittest 
from app import create_app
from app.models import db, Mechanic, Service_Ticket, Customer
from app.utils.util import encode_token
from marshmallow import ValidationError
from datetime import date

class TestMechanic(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.customer = Customer(
                name='Test Customer',
                email='testcustomer@example.com',
                phone='123-456-7890',
                password='123456'
            )
            db.session.add(self.customer)
            db.session.commit()
            self.mechanic = Mechanic(
                name='Test Mechanic', 
                email='testmech@example.com', 
                phone='123-456-7890', 
                salary="50000",
                password='123456')
            db.session.add(self.mechanic)
            db.session.commit() 
            self.mechanic_id = self.mechanic.id
            self.service_ticket = Service_Ticket(
                VIN='TESTVIN123',
                service_date=date(2025, 1, 1),
                service_desc='Oil Change',
                customer_id=self.customer.id  
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            self.ticket_id = self.service_ticket.id
            self.token = encode_token(self.mechanic.id, user_type='mechanic')
        
        
    # Mechanic Login (with token) Test - ⚡ Tested!
    def test_login_mechanic(self): 
        payload = {
            'email': 'testmech@example.com',
            'password': '123456'
        }
        response = self.client.post('/mechanics/login', json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        
    # Negative Test - Wrong Password ⚡ Tested! 
    def test_invalid_login(self):  
        bad_payload = {
            "email": "testmech@example.com",
            "password": "wrongpassword"
        }
        response_bad = self.client.post('/mechanics/login', json=bad_payload)
        self.assertEqual(response_bad.status_code, 401)
        self.assertIn('message', response_bad.json) 
    
    # Create a Mechanic Test - ⚡ Tested!
    def test_create_mechanic(self):
        payload = {
            "name": "Mechanic Mike",
            "email": "mm1@gmail.com",
            "phone": "562-713-9999",
            "salary": "67000",
            "password": "123456"
        }
        
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['name'], payload['name'])
    
    # Negative Test - Missing Phone Information ⚡ Tested! 
    def test_invalid_create_mechanic(self):
        payload = {
            "name": "Mechanic Mike",
            "email": "mm2@gmail.com",
            "salary": "67000",
            "password": "123456"
        }
        
        response = self.client.post('/mechanics/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.json)
        
    # Get All Mechanics Test - ⚡ Tested!
    def test_get_mechanic(self):
        response = self.client.get('/mechanics/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['name'], 'Test Mechanic')
        
    # Negative Test - Invalid pagination parameters ⚡ Tested!
    def test_invalid_get_mechanic(self):
        bad_response = self.client.get('/mechanics/?page=abc&per_page=xyz')
        self.assertEqual(bad_response.status_code, 200)
        self.assertEqual(len(bad_response.json), 1)
        self.assertEqual(bad_response.json[0]['name'], 'Test Mechanic')
        
    # Get a Specific Mechanic Test -⚡ Tested!
    def test_get_specific_mechanic(self):
        response = self.client.get('/mechanics/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], 'Test Mechanic')
        
    # Negative Test - Non-Existent Mechanic ⚡ Tested!
    def test_invalid_get_specific_mechanic(self):
        response_bad = self.client.get('/mechanics/999')
        self.assertEqual(response_bad.status_code, 404)
        self.assertIn('error', response_bad.json)
    
    # Update a Specific Mechanic Test - ⚡ Tested!
    def test_mechanic_update(self): 
        update_payload = {
            'name': 'Updated Mechanic',
            'email':'testmech@email.com',
            'phone':'123-456-7890',
            'salary': "60000",
            'password': '123456'
        }
        
        headers = {'Authorization':'Bearer ' + self.token}
        response = self.client.put('/mechanics/', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], update_payload['name'])
        
    # Negative Test - Invalid Data / Missing Salary - ⚡ Tested!
    def test_invalid_mechanic_update(self): 
        invalid_payload =  {
            "name": "Mechanic Tom",
            "email": "mm56@gmail.com",
            "phone": "562-713-8888",
            "password": "123456"
            }
        headers={"Authorization": f"Bearer {self.token}"}
        response = self.client.put('/mechanics/', json=invalid_payload, headers=headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn('salary', response.json)
        
    # Delete a Specific Mechanic Test - ⚡ Tested!
    def test_delete_mechanic(self):
        headers={"Authorization": f"Bearer {self.token}"}
        mechanic_id = self.mechanic.id
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
        response.json['message'],
        f"Mechanic id: {self.mechanic.id} successfully deleted."
        )
        
    # Negative Test - Already Deleted Mechanic - ⚡ Tested!
    def test_invalid_delete_mechanic(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        self.client.delete('/mechanics/', headers=headers)
        response = self.client.delete('/mechanics/', headers=headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json)
    
    # Add Mechanic to Service Ticket Test - ⚡ Tested!
    def test_add_mechanic_to_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.client.post(f'/mechanics/{self.mechanic_id}/add-ticket/{self.ticket_id}', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(
            response.json['message'],
            f"Mechanic {self.mechanic_id} assigned to ticket {self.ticket_id}."
        )
        
    # Negative Test - Mechanic Already Added  - ⚡ Tested!
    def test_invalid_add_mechanic_to_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        self.client.post(f'/mechanics/{self.mechanic_id}/add-ticket/{self.ticket_id}', headers=headers)
        response_bad = self.client.post(f'/mechanics/{self.mechanic_id}/add-ticket/{self.ticket_id}', headers=headers)
        self.assertEqual(response_bad.status_code, 200)
        self.assertIn('message', response_bad.json)
        self.assertEqual(
            response_bad.json['message'],
            "Mechanic is already assigned to this ticket."
        )

    # Remove Mechanic From Service Ticket Test - ⚡ Tested!
    def test_remove_mechanic_from_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        with self.app.app_context():
            ticket = db.session.get(Service_Ticket, self.ticket_id)
            mechanic = db.session.get(Mechanic, self.mechanic_id)
            if mechanic not in ticket.mechanics:
                ticket.mechanics.append(mechanic)
                db.session.commit()
        response = self.client.delete(f'/mechanics/{self.mechanic_id}/remove-ticket/{self.ticket_id}', headers=headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.json)
        self.assertEqual(
            response.json['message'],
            f"Mechanic {self.mechanic_id} removed from ticket {self.ticket_id}."
        )
        with self.app.app_context():
            ticket = db.session.get(Service_Ticket, self.ticket_id)
            self.assertNotIn(mechanic, ticket.mechanics)

    # Negative Test - Mechanic Not Assigned - ⚡ Tested!
    def test_invalid_remove_mechanic_from_ticket(self):
        headers = {'Authorization': f'Bearer {self.token}'}

        with self.app.app_context():
            ticket = db.session.get(Service_Ticket, self.ticket_id)
            mechanic = db.session.get(Mechanic, self.mechanic_id)
            if mechanic in ticket.mechanics:
                ticket.mechanics.remove(mechanic)
                db.session.commit()
        response_bad = self.client.delete(
            f'/mechanics/{self.mechanic_id}/remove-ticket/{self.ticket_id}',
            headers=headers
        )
        self.assertIn(response_bad.status_code, [200, 400, 404])
        self.assertIn('message', response_bad.json)
        self.assertEqual(
            response_bad.json['message'],
            "Mechanic is not assigned to this ticket."
        )
    
    # Get Mechanics Who Have Worked on the Most Tickets - ⚡ Tested!
    def test_get_popular_mechanic(self):
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(m['name'] == 'Test Mechanic' for m in response.json))
        
    # Negative Test - No Mechanics in Database - ⚡ Tested!
    def test_invalid_get_popular_mechanic(self):
        with self.app.app_context():
            db.session.query(Mechanic).delete()
            db.session.commit()
        response = self.client.get('/mechanics/popular')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])