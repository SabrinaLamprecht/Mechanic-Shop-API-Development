# /app/models.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import date
from typing import List 

# Create a base class for the models
class Base(DeclarativeBase):
    pass

# Instantiate the SQLAlchemy database
db = SQLAlchemy(model_class = Base)

# Junction table - Created for the many-to many relationship to establish a connection between
# services and mechanics 
service_mechanics = db.Table(
    'service_mechanics',
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
    phone: Mapped[str] = mapped_column(db.String(25), nullable=False)
    
    # Relationship attribute
    service_tickets: Mapped[List['Service_Ticket']] = db.relationship(back_populates="customer")
    
    
# Creating the Service_Ticket Model
class Service_Ticket(Base):
    __tablename__ = 'service_tickets'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    VIN: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    service_date: Mapped[date] = mapped_column(db.Date)
    service_desc: Mapped[str] = mapped_column(db.String(360), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id')) 
    
    # Relationship attribute
    customer: Mapped['Customer'] = db.relationship(back_populates="service_tickets")  
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=service_mechanics, back_populates='service_tickets')
 
# Creating the Mechanics Model
class Mechanic(Base): 
    __tablename__ = 'mechanics'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(db.String(25), nullable=False)
    salary: Mapped[str] = mapped_column(db.String(12), nullable=False)
    
    service_tickets: Mapped[List['Service_Ticket']] = db.relationship(secondary=service_mechanics, back_populates='mechanics')


