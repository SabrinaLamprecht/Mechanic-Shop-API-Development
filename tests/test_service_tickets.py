# /tests/test_service_tickets.py

import unittest 
from app import create_app
from app.models import db, Inventory, Mechanic, Service_Ticket, Customer
from app.utils.util import encode_token
from marshmallow import ValidationError
from datetime import date

class TestService_Ticket(unittest.TestCase):
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
            self.customer_id = self.customer.id
            self.customer_token = encode_token(self.customer_id, user_type='customer')
            self.inventory = Inventory(
                part_name='Test Part',
                price='29.99')
            db.session.add(self.inventory)
            db.session.commit()
            self.part_id = self.inventory.id
            self.mechanic1 = Mechanic(
                name='Mechanic 1', 
                email='mech1@example.com', 
                phone='123-456-7890', 
                salary="50000",
                password='123456')
            self.mechanic2 = Mechanic(
                name='Mechanic 2',
                email='mech2@example.com',
                phone='111-222-3333',
                salary="40000",
                password='123456'
            )
            self.mechanic3 = Mechanic(
                name='Mechanic 3',
                email='mech3@example.com',
                phone='222-333-4444',
                salary="45000",
                password='123456'
            )
            db.session.add_all([self.mechanic1, self.mechanic2, self.mechanic3])
            db.session.commit()
            
            self.mechanic1_id = self.mechanic1.id
            self.mechanic2_id = self.mechanic2.id
            self.mechanic3_id = self.mechanic3.id
            
            self.mechanic_id = self.mechanic1.id  # for token
            self.token = encode_token(self.mechanic_id, user_type='mechanic')
            self.service_ticket = Service_Ticket(
                VIN='TESTVIN123',
                service_date=date(2025, 1, 1),
                service_desc='Oil Change',
                customer_id=self.customer.id  
            )
            db.session.add(self.service_ticket)
            db.session.commit()
            self.ticket_id = self.service_ticket.id
            self.token = encode_token(self.mechanic1.id, user_type='mechanic')
    
# Create a Service Ticket Test - ⚡ Tested!
    def test_create_ticket(self):
        payload = {
            "VIN" :'TESTVIN124',
            "service_date" : "2025-01-01",
            "service_desc" :'Oil Change',
            "customer_id" : self.customer_id  
        }  
        response = self.client.post('/service_tickets/', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
    
    # Negative Test - Missing Service_Date Information ⚡ Tested! 
    def test_create_ticket_missing_date(self): 
        payload = {
            "VIN" :'TESTVIN125',
            "service_desc" :'Oil Change',
            "customer_id" : self.customer_id  
        }  
        response = self.client.post('/service_tickets/', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('service_date', response.json)
        
    # Get All Service Tickets Test - ⚡ Tested!
    def test_get_tickets(self):
        response = self.client.get('/service_tickets/?page=1&per_page=10')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json[0]['VIN'], 'TESTVIN123')
        
    # Negative Test - Invalid pagination parameters ⚡ Tested!
    def test_invalid_get_tickets(self):
        bad_response = self.client.get('/service_tickets/?page=abc&per_page=xyz')
        self.assertEqual(bad_response.status_code, 200)
        self.assertEqual(len(bad_response.json), 1)
        self.assertEqual(bad_response.json[0]['VIN'], 'TESTVIN123')
        
    # Get a Specific Service Ticket Test -⚡ Tested!
    def test_get_specific_ticket(self):
        response = self.client.get(f'/service_tickets/{self.ticket_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['VIN'], 'TESTVIN123')
        
    # Negative Test - Non-Existent Service Ticket -⚡ Tested!
    def test_invalid_get_specific_ticket(self):
        response_bad = self.client.get('/service_tickets/999')
        self.assertEqual(response_bad.status_code, 404)
        self.assertIn('error', response_bad.json)
        
    
    # Update a Service Ticket by Adding or Removing Mechanic(s) Test -⚡ Tested!
    def test_add_or_remove_mechanic(self):
        update_payload = {
            'add_ids': [self.mechanic1_id, self.mechanic3_id],
            'remove_ids': [self.mechanic2_id]
        }
        response = self.client.put(
            f'/service_tickets/{self.ticket_id}', 
            json=update_payload
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            ticket = db.session.get(Service_Ticket, self.ticket_id)
            mechanic_ids = {m.id for m in ticket.mechanics}
        added_ids = {self.mechanic1_id, self.mechanic3_id}
        removed_id = self.mechanic2_id
        for added in added_ids:
            self.assertIn(added, mechanic_ids)
        self.assertNotIn(removed_id, mechanic_ids)
        
    # Negative Test - Invalid Data  -⚡ Tested!
    def test_invalid_add_or_remove_mechanic(self): 
        invalid_payload =  {
            'add_ids': [self.mechanic1_id, self.mechanic3_id]
            }
        response = self.client.put(f'/service_tickets/{self.ticket_id}', json=invalid_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('remove_ids', response.json)
    
    # Get All Service Tickets for a Specific Customer Test -⚡ Tested!
    def test_get_my_tickets(self):
        headers={"Authorization": f"Bearer {self.customer_token}"}
        response = self.client.get(f'/service_tickets/my-tickets', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertEqual(response.json[0]['VIN'], 'TESTVIN123')
        
    # Negative Test - Non-Existent Service Ticket -⚡ Tested!
    def test_invalid_get_my_tickets(self):
        with self.app.app_context():
            new_customer = Customer(
                name='NoTicketCustomer',
                email='noticket@example.com',
                phone='000-000-0000',
                password='123456'
            )
            db.session.add(new_customer)
            db.session.commit()
            new_token = encode_token(new_customer.id, user_type='customer')

        headers = {"Authorization": f"Bearer {new_token}"}
        response_bad = self.client.get('/service_tickets/my-tickets', headers=headers)
    
        self.assertEqual(response_bad.status_code, 200)  # list returned, empty if no tickets
        self.assertEqual(len(response_bad.json), 0)
        
    
    # Update a Service Ticket by Adding a Part Test
    def test_add_part_to_ticket(self):
        update_payload = {
            'part_id': self.part_id}
        response = self.client.put(
            f'/service_tickets/{self.ticket_id}/add-part', 
            json=update_payload
        )
        self.assertEqual(response.status_code, 200)
        
    # Negative Test - Invalid Data  -⚡ Tested!
    def test_invalid_add_part_to_ticket(self): 
        invalid_payload =  {
            'part_name': 2
            }
        response = self.client.put(f'/service_tickets/{self.ticket_id}/add-part', json=invalid_payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn('part_id', response.json)
    