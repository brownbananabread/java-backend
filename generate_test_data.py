#!/usr/bin/env python3
"""
Generate random test data for the Event Management System database.
Uses SQLAlchemy ORM and Faker for simplified data generation.
"""

import random
import json
from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import click

# Initialize Faker for Australian locale
fake = Faker('en_AU')

# Database connection string
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/testing"

# Constants for data generation
EVENT_CATEGORIES = ['conference', 'music', 'networking', 'workshop', 'sports', 
                   'exhibition', 'seminar', 'festival', 'other']

TICKET_TYPES = ['general', 'vip', 'premium']
TICKET_STATUSES = ['registered', 'pending', 'rejected', 'refunded']

SYDNEY_VENUES = [
    ('Sydney Convention Centre', 'Darling Harbour, Sydney NSW'),
    ('Sydney Opera House', 'Bennelong Point, Sydney NSW'),
    ('Royal Botanic Gardens', 'Mrs Macquaries Rd, Sydney NSW'),
    ('ICC Sydney', '14 Darling Dr, Sydney NSW'),
    ('Qudos Bank Arena', 'Olympic Blvd, Sydney Olympic Park NSW'),
    ('Sydney Showground', '1 Showground Rd, Sydney Olympic Park NSW'),
    ('UTS Great Hall', '15 Broadway, Ultimo NSW'),
    ('Bondi Pavilion', 'Queen Elizabeth Dr, Bondi Beach NSW'),
]

EVENT_NAMES = {
    'conference': ['Tech Summit', 'AI Conference', 'Digital Forum', 'Innovation Expo'],
    'music': ['Summer Festival', 'Jazz Night', 'Rock Concert', 'Symphony Orchestra'],
    'networking': ['Business Mixer', 'Startup Meetup', 'Professional Network', 'Industry Connect'],
    'workshop': ['Coding Bootcamp', 'Design Workshop', 'Photography Class', 'Writing Masterclass'],
    'sports': ['City Marathon', 'Tennis Open', 'Swimming Championship', 'Cycling Tour'],
    'exhibition': ['Art Gallery', 'Photo Exhibition', 'Design Showcase', 'Trade Show'],
    'seminar': ['Leadership Talk', 'Marketing Seminar', 'Finance Workshop', 'Health Forum'],
    'festival': ['Food Festival', 'Cultural Fair', 'Street Festival', 'Wine Tasting'],
    'other': ['Community Event', 'Charity Gala', 'Awards Night', 'Special Event']
}


class DataGenerator:
    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=engine)
        self.organizer_ids = []
        self.attendee_ids = []
        self.event_ids = []
        
    def clear_existing_data(self):
        """Clear existing data from all tables"""
        with self.engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE activity, tickets, events, users RESTART IDENTITY CASCADE"))
            conn.commit()
            
    def generate_users(self, num_organizers=10, num_attendees=50):
        """Generate both organizers and attendees"""
        session = self.Session()
        
        # Generate organizers
        click.echo(f"Creating {num_organizers} organizers...")
        for _ in range(num_organizers):
            org_data = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.unique.email(),
                'password': 'password123',  # Simple password for testing
                'role': 'organizer',
                'phone': fake.phone_number(),
                'organization': fake.company(),
                'bio': fake.text(max_nb_chars=200),
                'ratings': [],
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            result = session.execute(
                text("""INSERT INTO users (first_name, last_name, email, password, role, 
                       phone, organization, bio, ratings, created_at, updated_at)
                       VALUES (:first_name, :last_name, :email, :password, :role,
                       :phone, :organization, :bio, :ratings, :created_at, :updated_at)
                       RETURNING user_id"""),
                org_data
            )
            self.organizer_ids.append(result.scalar())
        
        # Generate attendees
        click.echo(f"Creating {num_attendees} attendees...")
        for _ in range(num_attendees):
            attendee_data = {
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'email': fake.unique.email(),
                'password': 'password123',
                'role': 'attendee',
                'phone': fake.phone_number(),
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            result = session.execute(
                text("""INSERT INTO users (first_name, last_name, email, password, role, 
                       phone, created_at, updated_at)
                       VALUES (:first_name, :last_name, :email, :password, :role,
                       :phone, :created_at, :updated_at)
                       RETURNING user_id"""),
                attendee_data
            )
            self.attendee_ids.append(result.scalar())
        
        session.commit()
        session.close()
        
    def generate_events(self, num_events=20):
        """Generate events"""
        session = self.Session()
        
        click.echo(f"Creating {num_events} events...")
        for _ in range(num_events):
            category = random.choice(EVENT_CATEGORIES)
            venue_name, location = random.choice(SYDNEY_VENUES)
            
            # Generate prices
            general_price = random.choice([0, 25, 45, 65, 85, 95, 125, 149])
            vip_price = int(general_price * random.uniform(1.5, 2.5)) if general_price > 0 else random.choice([75, 100, 150])
            premium_price = int(general_price * random.uniform(2.5, 4.0)) if general_price > 0 else random.choice([150, 200, 300])
            
            event_data = {
                'organizer_id': random.choice(self.organizer_ids),
                'title': f"{random.choice(EVENT_NAMES[category])} {datetime.now().year}",
                'description': fake.text(max_nb_chars=500),
                'category': category,
                'datetime': fake.date_time_between(start_date='+1w', end_date='+6M'),
                'location': location,
                'venue_name': venue_name,
                'max_capacity': random.randint(50, 2000),
                'current_registrations': 0,
                'general_price': Decimal(str(general_price)),
                'vip_price': Decimal(str(vip_price)),
                'premium_price': Decimal(str(premium_price)),
                'status': 'active',
                'requirements': fake.sentence() if random.random() > 0.7 else None,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            result = session.execute(
                text("""INSERT INTO events (organizer_id, title, description, category, datetime,
                       location, venue_name, max_capacity, current_registrations,
                       general_price, vip_price, premium_price, status, requirements,
                       created_at, updated_at)
                       VALUES (:organizer_id, :title, :description, :category, :datetime,
                       :location, :venue_name, :max_capacity, :current_registrations,
                       :general_price, :vip_price, :premium_price, :status, :requirements,
                       :created_at, :updated_at)
                       RETURNING event_id"""),
                event_data
            )
            self.event_ids.append(result.scalar())
        
        session.commit()
        session.close()
        
    def generate_tickets(self, num_tickets=50):
        """Generate ticket registrations"""
        session = self.Session()
        
        click.echo(f"Creating {num_tickets} tickets...")
        
        # Get event prices
        event_prices = {}
        for event_id in self.event_ids:
            result = session.execute(
                text("SELECT general_price, vip_price, premium_price FROM events WHERE event_id = :event_id"),
                {'event_id': event_id}
            ).fetchone()
            event_prices[event_id] = result
        
        for _ in range(num_tickets):
            event_id = random.choice(self.event_ids)
            user_id = random.choice(self.attendee_ids)
            ticket_type = random.choice(TICKET_TYPES)
            status = random.choices(TICKET_STATUSES, weights=[80, 15, 3, 2])[0]
            
            # Get user details for ticket
            user = session.execute(
                text("SELECT first_name, last_name, email FROM users WHERE user_id = :user_id"),
                {'user_id': user_id}
            ).fetchone()
            
            # Determine price
            price_index = {'general': 0, 'vip': 1, 'premium': 2}[ticket_type]
            price_paid = event_prices[event_id][price_index]
            
            ticket_data = {
                'event_id': event_id,
                'user_id': user_id,
                'ticket_type': ticket_type,
                'status': status,
                'price_paid': price_paid,
                'booking_reference': f"EVT-{fake.unique.random_number(digits=10)}",
                'payment_id': f"pay_{fake.uuid4()[:8]}" if status in ['registered', 'refunded'] else None,
                'special_requests': fake.sentence() if random.random() > 0.8 else None,
                'quantity': 1,
                'customer_name': f"{user[0]} {user[1]}",
                'customer_email': user[2],
                'purchase_date': fake.date_time_between(start_date='-30d', end_date='now'),
                'checked_in': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            session.execute(
                text("""INSERT INTO tickets (event_id, user_id, ticket_type, status, price_paid,
                       booking_reference, payment_id, special_requests, quantity,
                       customer_name, customer_email, purchase_date, checked_in,
                       created_at, updated_at)
                       VALUES (:event_id, :user_id, :ticket_type, :status, :price_paid,
                       :booking_reference, :payment_id, :special_requests, :quantity,
                       :customer_name, :customer_email, :purchase_date, :checked_in,
                       :created_at, :updated_at)"""),
                ticket_data
            )
        
        # Update event registration counts
        session.execute(
            text("""UPDATE events SET current_registrations = (
                    SELECT COUNT(*) FROM tickets 
                    WHERE tickets.event_id = events.event_id 
                    AND tickets.status = 'registered'
                )""")
        )
        
        session.commit()
        session.close()
        
    def generate_activities(self):
        """Generate activity logs"""
        session = self.Session()
        
        click.echo("Creating activity logs...")
        
        # Log event creation activities
        for event_id in self.event_ids[:10]:
            event = session.execute(
                text("SELECT title, organizer_id FROM events WHERE event_id = :event_id"),
                {'event_id': event_id}
            ).fetchone()
            
            activity_data = {
                'user_id': event[1],
                'event_id': event_id,
                'activity_type': 'event_created',
                'description': f"Created new event: {event[0]}",
                'metadata': json.dumps({}),  # Convert dict to JSON string
                'created_at': fake.date_time_between(start_date='-30d', end_date='now')
            }
            
            session.execute(
                text("""INSERT INTO activity (user_id, event_id, activity_type,
                       description, metadata, created_at)
                       VALUES (:user_id, :event_id, :activity_type,
                       :description, :metadata, :created_at)"""),
                activity_data
            )
        
        # Log ticket booking activities
        tickets = session.execute(
            text("""SELECT t.ticket_id, t.user_id, t.event_id, e.title, t.ticket_type
                   FROM tickets t
                   JOIN events e ON t.event_id = e.event_id
                   WHERE t.status = 'registered'
                   LIMIT 20""")
        ).fetchall()
        
        for ticket in tickets:
            activity_data = {
                'user_id': ticket[1],
                'event_id': ticket[2],
                'ticket_id': ticket[0],
                'activity_type': 'ticket_booked',
                'description': f"{ticket[4].title()} registration for {ticket[3]}",
                'metadata': json.dumps({}),  # Convert dict to JSON string
                'created_at': fake.date_time_between(start_date='-20d', end_date='now')
            }
            
            session.execute(
                text("""INSERT INTO activity (user_id, event_id, ticket_id, activity_type,
                       description, metadata, created_at)
                       VALUES (:user_id, :event_id, :ticket_id, :activity_type,
                       :description, :metadata, :created_at)"""),
                activity_data
            )
        
        session.commit()
        session.close()


@click.command()
@click.option('--organizers', default=10, help='Number of organizers to create')
@click.option('--attendees', default=50, help='Number of attendees to create')
@click.option('--events', default=20, help='Number of events to create')
@click.option('--tickets', default=50, help='Number of tickets to create')
@click.option('--clear', is_flag=True, help='Clear existing data before generating')
def main(organizers, attendees, events, tickets, clear):
    """Generate test data for the Event Management System"""
    
    click.echo("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    generator = DataGenerator(engine)
    
    if clear:
        click.echo("Clearing existing data...")
        generator.clear_existing_data()
    
    try:
        generator.generate_users(organizers, attendees)
        generator.generate_events(events)
        generator.generate_tickets(tickets)
        generator.generate_activities()
        
        click.echo(click.style("\n✓ Test data generation complete!", fg='green'))
        click.echo(f"  - {organizers} organizers")
        click.echo(f"  - {attendees} attendees")
        click.echo(f"  - {events} events")
        click.echo(f"  - {tickets} tickets")
        
    except Exception as e:
        click.echo(click.style(f"\n✗ Error: {str(e)}", fg='red'))
        raise


if __name__ == '__main__':
    main()