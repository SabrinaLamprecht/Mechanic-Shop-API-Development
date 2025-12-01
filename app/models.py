# /app/models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date, datetime
from typing import List 

# Create a base class for the models
class Base(DeclarativeBase):
    pass

# Instantiate the SQLAlchemy database
db = SQLAlchemy(model_class = Base)

# Junction table - Created for the many-to many relationship to establish a connection between
# services and mechanics 
service_mechanic = db.Table(
    'service_mechanic',
    Base.metadata,
    db.Column('ticket_id', db.ForeignKey('service_tickets.id')),
    db.Column('mechanic_id', db.ForeignKey('mechanics.id'))
)

# Creating the Customer Model
class Customer(Base):
    __tablename__ = 'customers'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    # Relationship attribute
    service_tickets: Mapped[List['Service_Ticket']] = db.relationship(back_populates="customer")
    
    
# Creating the Service_Ticket Model
class Service_Ticket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(db.Date, nullable=False)
    service_desc: Mapped[str] = mapped_column(db.String(360), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'), nullable=False) 
    
    # Relationship attribute
    customer: Mapped['Customer'] = db.relationship(back_populates="service_tickets")  
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanic, back_populates='service_tickets')
    mechanic_tickets: Mapped[List["MechanicServiceTicket"]] = db.relationship(back_populates="service_ticket")
    service_ticket_inventory: Mapped[List["ServiceTicketInventory"]] = db.relationship(back_populates='service_ticket')
 
# Creating the Mechanics Model
class Mechanic(Base): 
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(25), nullable=False)
    salary: Mapped[float] = mapped_column(db.String(12), nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    service_tickets: Mapped[List['Service_Ticket']] = db.relationship(secondary=service_mechanic, back_populates='mechanics')
    mechanic_tickets: Mapped[List["MechanicServiceTicket"]] = db.relationship(back_populates='mechanic')

# Complex Many to Many Relationship
class MechanicServiceTicket(Base):
    __tablename__ = "MechanicServiceTicket"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    mechanic_id: Mapped[int] = mapped_column(db.ForeignKey("mechanics.id"), nullable=False)
    service_id: Mapped[int] = mapped_column(db.ForeignKey("service_tickets.id"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    mechanic: Mapped['Mechanic'] = db.relationship(back_populates='mechanic_tickets')
    service_ticket: Mapped["Service_Ticket"] = db.relationship(back_populates='mechanic_tickets')

# Creating the Inventory Model - Establish a many-to-many relationship from Inventory 
# to ServiceTicket, as One ticket can require many parts, and the same kind of part can be 
# used on many different tickets.
class Inventory(Base): 
    __tablename__ = 'inventory'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    part_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float(), nullable=False)
    
    service_ticket_inventory: Mapped[List["ServiceTicketInventory"]] = db.relationship(back_populates='inventory')
    

class ServiceTicketInventory(Base):
    __tablename__ = "service_ticket_inventory"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_id: Mapped[int] = mapped_column(db.ForeignKey('inventory.id'), nullable=False)
    service_ticket_id: Mapped[int] = mapped_column(db.ForeignKey('service_tickets.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    
    inventory: Mapped['Inventory'] = db.relationship(back_populates='service_ticket_inventory')
    service_ticket: Mapped['Service_Ticket'] = db.relationship(back_populates='service_ticket_inventory')