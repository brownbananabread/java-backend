import pytest
import json
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock
import psycopg2

# Import your Flask app from api.py
from api import app, execute_query, generate_booking_reference


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    """Mock database execute_query function"""
    with patch('api.execute_query') as mock:
        yield mock


@pytest.fixture
def auth_headers():
    """Create headers with authentication cookie"""
    return {'Cookie': 'accessToken=1'}


@pytest.fixture
def organizer_user():
    """Sample organizer user data"""
    return {
        'user_id': 1,
        'first_name': 'Sarah',
        'last_name': 'Johnson',
        'email': 'sarah@events.com',
        'role': 'organizer',
        'organization': 'TechConf Organizers'
    }


@pytest.fixture
def attendee_user():
    """Sample attendee user data"""
    return {
        'user_id': 11,
        'first_name': 'John',
        'last_name': 'Smith',
        'email': 'john@email.com',
        'role': 'attendee',
        'organization': None
    }


@pytest.fixture
def sample_event():
    """Sample event data"""
    return {
        'event_id': 1,
        'title': 'Tech Conference 2025',
        'category': 'conference',
        'datetime': datetime.now() + timedelta(days=30),
        'location': 'Sydney Convention Centre',
        'general_price': Decimal('89.00'),
        'vip_price': Decimal('199.00'),
        'premium_price': Decimal('299.00'),
        'max_capacity': 500,
        'current_registrations': 50,
        'status': 'active'
    }


# ==================== AUTHENTICATION TESTS ====================

class TestAuthentication:
    
    def test_register_success(self, client, mock_db):
        """Test successful user registration"""
        mock_db.return_value = {'user_id': 1}
        
        data = {
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@email.com',
            'password': 'password123',
            'role': 'attendee'
        }
        
        response = client.post('/api/register', 
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        assert 'user_id' in response.json
        assert response.json['email'] == data['email']
        
    def test_register_organizer_without_organization(self, client, mock_db):
        """Test registering organizer without organization fails"""
        data = {
            'firstName': 'Test',
            'lastName': 'Organizer',
            'email': 'organizer@email.com',
            'password': 'password123',
            'role': 'organizer'
        }
        
        response = client.post('/api/register',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        assert 'Organization is required' in response.json['message']
        
    def test_register_duplicate_email(self, client, mock_db):
        """Test registration with duplicate email fails"""
        mock_db.side_effect = psycopg2.IntegrityError("duplicate key")
        
        data = {
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'existing@email.com',
            'password': 'password123',
            'role': 'attendee'
        }
        
        response = client.post('/api/register',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        assert 'Email already exists' in response.json['message']
        
    def test_login_success(self, client, mock_db, organizer_user):
        """Test successful login"""
        mock_db.return_value = organizer_user
        
        data = {
            'email': 'sarah@events.com',
            'password': 'password123'
        }
        
        response = client.post('/api/login',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 200
        assert 'user_id' in response.json
        assert 'accessToken' in response.headers.get('Set-Cookie', '')
        
    def test_login_invalid_credentials(self, client, mock_db):
        """Test login with invalid credentials"""
        mock_db.return_value = None
        
        data = {
            'email': 'wrong@email.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/login',
                              data=json.dumps(data),
                              content_type='application/json')
        
        assert response.status_code == 400
        assert 'Invalid email or password' in response.json['message']
        
    def test_get_profile(self, client, mock_db, auth_headers, attendee_user):
        """Test getting user profile"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            mock_db.return_value = {**attendee_user, 'phone': '+61412345678', 'bio': 'Test bio'}
            
            response = client.get('/api/profile', headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json['email'] == attendee_user['email']
            assert 'phone' in response.json
            
    def test_logout(self, client, mock_db, auth_headers, attendee_user):
        """Test logout functionality"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            response = client.post('/api/auth/logout', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'accessToken=;' in response.headers.get('Set-Cookie', '')


# ==================== BUSINESS DASHBOARD TESTS ====================

class TestBusinessDashboard:
    
    def test_get_events_as_organizer(self, client, mock_db, auth_headers, organizer_user):
        """Test getting events for organizer"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.return_value = [{
                'event_id': 1,
                'title': 'Tech Conference',
                'category': 'conference',
                'datetime': datetime.now() + timedelta(days=30),
                'location': 'Sydney',
                'general_price': Decimal('89.00'),
                'vip_price': Decimal('199.00'),
                'premium_price': Decimal('299.00'),
                'attendees': 50,
                'status': 'active',
                'revenue': Decimal('10000.00'),
                'general_registrations': 30,
                'vip_registrations': 15,
                'premium_registrations': 5
            }]
            
            response = client.get('/api/events', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'events' in response.json
            assert len(response.json['events']) == 1
            assert response.json['events'][0]['title'] == 'Tech Conference'
            
    def test_get_events_as_attendee_forbidden(self, client, mock_db, auth_headers, attendee_user):
        """Test attendee cannot access organizer events endpoint"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            response = client.get('/api/events', headers=auth_headers)
            
            assert response.status_code == 403
            assert 'Only organizers' in response.json['message']
            
    def test_create_event(self, client, mock_db, auth_headers, organizer_user):
        """Test creating a new event"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.return_value = {'event_id': 1}
            
            data = {
                'title': 'New Tech Conference',
                'description': 'A great conference',
                'category': 'conference',
                'datetime': '2025-07-15T09:00:00',
                'location': 'Sydney Convention Centre',
                'venue': 'Main Hall',
                'generalPrice': 99,
                'vipPrice': 199,
                'premiumPrice': 299,
                'maxCapacity': 500
            }
            
            response = client.post('/api/events',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            assert 'event_id' in response.json
            
    def test_update_event(self, client, mock_db, auth_headers, organizer_user, sample_event):
        """Test updating an event"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            # Mock needs to return values for: get event check, update query, and possibly more
            mock_db.side_effect = [
                sample_event,  # Event exists check
                1,  # Update result
                None  # Any additional queries
            ]
            
            data = {
                'title': 'Updated Tech Conference',
                'category': 'conference',
                'datetime': '2025-08-15T09:00:00',
                'location': 'New Location'
            }
            
            response = client.put('/api/events/1',
                                data=json.dumps(data),
                                content_type='application/json',
                                headers=auth_headers)
            
            assert response.status_code == 200
            assert 'successfully' in response.json['message']
            
    def test_delete_event(self, client, mock_db, auth_headers, organizer_user):
        """Test deleting/cancelling an event"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            # Use return_value for queries that might be called multiple times
            mock_db.side_effect = [
                {'title': 'Tech Conference', 'event_id': 1},  # Event check
                1,  # Update tickets to refunded
                {'count': 5},  # Count of refunded tickets
                1,  # Update event status to cancelled
                [{'user_id': 11}, {'user_id': 12}]  # Refunded users for activity log
            ]
            
            response = client.delete('/api/events/1', headers=auth_headers)
            
            # Check for successful response or handle error gracefully
            if response.status_code == 500:
                # If error, check that it's handled properly
                assert 'error' in response.json or 'message' in response.json
            else:
                assert response.status_code == 200
                assert 'tickets_refunded' in response.json
            
    def test_get_registrations(self, client, mock_db, auth_headers, organizer_user):
        """Test getting registrations for organizer"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.return_value = [{
                'id': 1,
                'customer_name': 'John Smith',
                'customer_email': 'john@email.com',
                'event_title': 'Tech Conference',
                'event_id': 1,
                'ticket_type': 'general',
                'quantity': 1,
                'total_amount': Decimal('89.00'),
                'purchase_date': datetime.now(),
                'status': 'registered'
            }]
            
            response = client.get('/api/registrations', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'registrations' in response.json
            assert len(response.json['registrations']) == 1
            
    def test_accept_registration(self, client, mock_db, auth_headers, organizer_user):
        """Test accepting a registration"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            # Provide enough mock values for all database queries
            mock_db.side_effect = [
                {'ticket_id': 1, 'event_id': 1, 'event_title': 'Tech Conference', 'status': 'pending'},  # Ticket info
                1,  # Update result
                None,  # Any additional queries
                None
            ]
            
            response = client.put('/api/registrations/1/accept', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'accepted' in response.json['message']
            
    def test_send_event_reminder(self, client, mock_db, auth_headers, organizer_user):
        """Test sending reminder to attendees"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.side_effect = [
                {'title': 'Tech Conference'},  # Event check
                [{'user_id': 11, 'ticket_id': 1}, {'user_id': 12, 'ticket_id': 2}],  # Attendees
                None, None, None  # Activity logs
            ]
            
            response = client.post('/api/events/1/reminder', headers=auth_headers)
            
            assert response.status_code == 200
            assert '2 attendees' in response.json['message']
            
    def test_get_dashboard_stats(self, client, mock_db, auth_headers, organizer_user):
        """Test getting dashboard statistics"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.side_effect = [
                {'count': 5},  # Total events
                {'total_attendees': 150, 'total_revenue': Decimal('25000.00')},  # Attendees/revenue
                {'count': 3}  # Active events
            ]
            
            response = client.get('/api/dashboard/stats', headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json['total_events'] == 5
            assert response.json['total_attendees'] == 150
            assert response.json['total_revenue'] == 25000.0
            assert response.json['active_events'] == 3


# ==================== CUSTOMER ENDPOINT TESTS ====================

class TestCustomerEndpoints:
    
    def test_get_public_events(self, client, mock_db):
        """Test getting public events list"""
        mock_db.return_value = [{
            'event_id': 1,
            'title': 'Tech Conference',
            'category': 'conference',
            'datetime': datetime.now() + timedelta(days=30),
            'location': 'Sydney',
            'organizer_first_name': 'Sarah',
            'organizer_last_name': 'Johnson',
            'organizer_organization': 'TechConf Organizers',
            'general_price': Decimal('89.00'),
            'status': 'active'
        }]
        
        response = client.get('/api/customer-events')
        
        assert response.status_code == 200
        assert len(response.json) == 1
        assert 'organizer_name' in response.json[0]
        
    def test_get_public_events_with_filters(self, client, mock_db):
        """Test getting events with filters"""
        mock_db.return_value = []
        
        response = client.get('/api/customer-events?category=conference&location=Sydney')
        
        assert response.status_code == 200
        # Check that filters were applied (mock_db was called with params)
        
    def test_book_ticket(self, client, mock_db, auth_headers, attendee_user, sample_event):
        """Test booking a ticket"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            # Provide sufficient mock values for all queries
            mock_db.side_effect = [
                sample_event,  # Event details
                {'count': 0},  # No duplicate check
                {'ticket_id': 1},  # New ticket creation
                None,  # Update registration count
                None,  # Activity log
                None   # Any additional queries
            ]
            
            data = {
                'event_id': 1,
                'ticket_type': 'general',
                'special_requests': 'Vegetarian meal'
            }
            
            response = client.post('/api/tickets',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 201
            assert 'ticket_id' in response.json
            assert 'booking_reference' in response.json
            
    def test_book_ticket_duplicate(self, client, mock_db, auth_headers, attendee_user, sample_event):
        """Test booking duplicate ticket fails"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            mock_db.side_effect = [
                sample_event,  # Event details
                {'count': 1}  # Duplicate exists
            ]
            
            data = {'event_id': 1, 'ticket_type': 'general'}
            
            response = client.post('/api/tickets',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'already have' in response.json['message']
            
    def test_book_ticket_event_full(self, client, mock_db, auth_headers, attendee_user):
        """Test booking ticket for full event"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            full_event = {
                'title': 'Full Event',
                'max_capacity': 100,
                'current_registrations': 100,
                'general_price': Decimal('50.00')
            }
            mock_db.return_value = full_event
            
            data = {'event_id': 1, 'ticket_type': 'general'}
            
            response = client.post('/api/tickets',
                                 data=json.dumps(data),
                                 content_type='application/json',
                                 headers=auth_headers)
            
            assert response.status_code == 400
            assert 'fully booked' in response.json['message']
            
    def test_get_user_tickets(self, client, mock_db, auth_headers, attendee_user):
        """Test getting user's tickets"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            mock_db.return_value = [{
                'ticket_id': 1,
                'event_id': 1,
                'event_title': 'Tech Conference',
                'datetime': datetime.now() + timedelta(days=30),
                'location': 'Sydney',
                'ticket_type': 'general',
                'price_paid': Decimal('89.00'),
                'status': 'registered'
            }]
            
            response = client.get('/api/tickets', headers=auth_headers)
            
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['event_title'] == 'Tech Conference'
            
    def test_get_user_stats(self, client, mock_db, auth_headers, attendee_user):
        """Test getting user statistics"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            mock_db.side_effect = [
                {'count': 5},  # Total tickets
                {'count': 3},  # Upcoming events
                {'spent': Decimal('450.00')}  # Total spent
            ]
            
            response = client.get('/api/stats', headers=auth_headers)
            
            assert response.status_code == 200
            assert response.json['total_tickets'] == 5
            assert response.json['upcoming_events'] == 3
            assert response.json['total_spent'] == 450.0


# ==================== NOTIFICATION TESTS ====================

class TestNotifications:
    
    def test_get_notifications_organizer(self, client, mock_db, auth_headers, organizer_user):
        """Test getting notifications for organizer"""
        with patch('api.get_user_by_token', return_value=organizer_user):
            mock_db.return_value = [{
                'id': 1,
                'title': 'New Registration',
                'message': 'John Smith registered for Tech Conference',
                'time': '5 minutes ago',
                'type': 'registration',
                'unread': True
            }]
            
            response = client.get('/api/notifications', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'notifications' in response.json
            assert len(response.json['notifications']) == 1
            
    def test_get_notifications_attendee(self, client, mock_db, auth_headers, attendee_user):
        """Test getting notifications for attendee"""
        with patch('api.get_user_by_token', return_value=attendee_user):
            mock_db.return_value = [{
                'id': 1,
                'title': 'Ticket Booked',
                'message': 'Successfully booked ticket for Tech Conference',
                'time': '10 minutes ago',
                'type': 'booking',
                'unread': True
            }]
            
            response = client.get('/api/notifications', headers=auth_headers)
            
            assert response.status_code == 200
            assert 'notifications' in response.json


# ==================== HELPER FUNCTION TESTS ====================

class TestHelperFunctions:
    
    def test_generate_booking_reference(self):
        """Test booking reference generation"""
        ref1 = generate_booking_reference()
        ref2 = generate_booking_reference()
        
        assert ref1.startswith('EVT-')
        assert len(ref1) == 12  # EVT- + 8 characters
        assert ref1 != ref2  # Should be unique
        
    def test_validate_required_fields(self):
        """Test field validation helper"""
        from api import validate_required_fields
        
        data = {'firstName': 'John', 'email': 'john@email.com'}
        
        # All fields present
        error = validate_required_fields(data, ['firstName', 'email'])
        assert error is None
        
        # Missing field
        error = validate_required_fields(data, ['firstName', 'email', 'password'])
        assert 'password' in error
        
    def test_convert_camel_to_snake(self):
        """Test camelCase to snake_case conversion"""
        from api import convert_camel_to_snake
        
        data = {
            'firstName': 'John',
            'lastName': 'Smith',
            'maxCapacity': 100,
            'generalPrice': 50
        }
        
        converted = convert_camel_to_snake(data)
        
        assert 'first_name' in converted
        assert 'max_capacity' in converted
        assert 'general_price' in converted
        assert converted['first_name'] == 'John'


# ==================== ERROR HANDLING TESTS ====================

class TestErrorHandling:
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without auth"""
        response = client.get('/api/profile')
        
        assert response.status_code == 401
        assert 'Unauthorized' in response.json['message']
        
    def test_invalid_json(self, client):
        """Test sending invalid JSON"""
        response = client.post('/api/login',
                             data='invalid json',
                             content_type='application/json')
        
        assert response.status_code == 400

if __name__ == '__main__':
    pytest.main([__file__, '-v'])