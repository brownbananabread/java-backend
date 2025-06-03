from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
import os
from functools import wraps
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

# Database configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'testing'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': os.getenv('DB_PORT', '5432')
}

# Global variable to track activities logged in current request
activities_logged = []

# ==================== LOGGING MIDDLEWARE ====================

@app.before_request
def log_request_start():
    """Log request details at the start"""
    global activities_logged
    activities_logged = []  # Reset for each request
    
    # Store request data for later use
    request.logged_data = {
        'method': request.method,
        'path': request.path,
        'body': request.get_json(silent=True) or {},
        'headers': dict(request.headers),
        'origin': request.environ.get('HTTP_ORIGIN', 'Unknown')
    }
    
    print("---------------")
    print(f"{request.method} {request.path}")
    print(f"body: {json.dumps(request.logged_data['body'], indent=2) if request.logged_data['body'] else '{}'}")
    print(f"headers: {json.dumps({k: v for k, v in request.logged_data['headers'].items() if k.lower() in ['content-type', 'authorization', 'cookie']}, indent=2)}")
    print(f"origin: {request.logged_data['origin']}")

@app.after_request
def log_request_end(response):
    """Log response details at the end"""
    global activities_logged
    
    # Get response data
    response_data = {}
    if response.content_type == 'application/json':
        try:
            response_data = json.loads(response.get_data(as_text=True))
        except:
            response_data = {"raw": response.get_data(as_text=True)}
    
    # Log activities
    print(f"activityLogged: {json.dumps(activities_logged, indent=2) if activities_logged else '[]'}")
    
    # Log response
    print(f"responseBody: {json.dumps(response_data, indent=2)}")
    print(f"responseCode: {response.status_code}")
    print("---------------\n")
    
    # Reset activities
    activities_logged = []
    
    return response

# ==================== HELPER FUNCTIONS ====================

def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
    """Execute database query with automatic connection management"""
    try:
        with psycopg2.connect(**DATABASE_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql, params or ())
                if fetch_one:
                    return cursor.fetchone()
                if fetch_all:
                    return cursor.fetchall()
                conn.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Database error: {str(e)}")
        return None

def log_activity(user_id, event_id, ticket_id, activity_type, description):
    """Log activity to database and tracking list"""
    global activities_logged
    
    sql = "INSERT INTO activity (user_id, event_id, ticket_id, activity_type, description) VALUES (%s, %s, %s, %s, %s)"
    execute_query(sql, (user_id, event_id, ticket_id, activity_type, description))
    
    # Track for request logging
    activities_logged.append({
        'user_id': user_id,
        'event_id': event_id,
        'ticket_id': ticket_id,
        'type': activity_type,
        'description': description
    })

def generate_booking_reference():
    """Generate unique booking reference"""
    return f"EVT-{str(uuid.uuid4())[:8].upper()}"

def get_access_token():
    """Get access token from cookies"""
    return request.cookies.get('accessToken')

def get_user_by_token(access_token):
    """Get user data by access token"""
    if not access_token:
        return None
    try:
        sql = "SELECT user_id, first_name, last_name, email, role, organization FROM users WHERE user_id = %s"
        return execute_query(sql, (int(access_token),), fetch_one=True)
    except ValueError:
        return None

def is_admin(access_token):
    """Check if user has admin privileges"""
    user = get_user_by_token(access_token)
    return user and user.get('role') == 'admin'

def is_organizer(access_token):
    """Check if user is an organizer"""
    user = get_user_by_token(access_token)
    return user and user.get('role') == 'organizer'

def create_response_with_cookie(data, access_token=None):
    """Create response with optional cookie"""
    response = make_response(jsonify(data))
    if access_token:
        response.set_cookie(
            'accessToken', str(access_token),
            max_age=24 * 60 * 60, httponly=False, path='/', samesite='Lax'
        )
    return response

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_user_by_token(get_access_token()):
            return jsonify({"message": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_admin(get_access_token()):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

def require_organizer(f):
    """Decorator to require organizer privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_organizer(get_access_token()):
            return jsonify({"message": "Only organizers can access this endpoint"}), 403
        return f(*args, **kwargs)
    return decorated

def validate_required_fields(data, required_fields):
    """Validate that all required fields are present"""
    missing = [field for field in required_fields if not data.get(field)]
    if missing:
        return f"Missing required fields: {', '.join(missing)}"
    return None

def convert_camel_to_snake(data):
    """Convert camelCase keys to snake_case for database operations"""
    if isinstance(data, dict):
        conversion_map = {
            'firstName': 'first_name',
            'lastName': 'last_name',
            'user_id': 'user_id',
            'event_id': 'event_id',
            'ticket_id': 'ticket_id',
            'startDate': 'datetime',  # Updated to use datetime
            'endDate': 'datetime',    # Updated to use datetime
            'date': 'datetime',       # Added for compatibility
            'maxCapacity': 'max_capacity',
            'venueName': 'venue_name',
            'generalPrice': 'general_price',
            'vipPrice': 'vip_price',
            'premiumPrice': 'premium_price',
            'imageUrl': 'image_url',
            'ticketType': 'ticket_type',
            'specialRequests': 'special_requests'
        }
        return {conversion_map.get(key, key): value for key, value in data.items()}
    return data

# ==================== USER AUTHENTICATION ENDPOINTS ====================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required = ['firstName', 'lastName', 'email', 'password', 'role']
    error = validate_required_fields(data, required)
    if error:
        return jsonify({"message": error}), 400
    
    # Special validation for organizers
    if data['role'] == 'organizer' and not data.get('organization', '').strip():
        return jsonify({"message": "Organization is required for organizers"}), 400
    
    # Insert user
    sql = """INSERT INTO users (first_name, last_name, email, password, role, organization, phone) 
             VALUES (%s, %s, %s, %s, %s::user_role, %s, %s) RETURNING user_id"""
    params = (data['firstName'], data['lastName'], data['email'], data['password'], 
              data['role'], data.get('organization'), data.get('phone'))
    
    try:
        result = execute_query(sql, params, fetch_one=True)
        if result:
            user_id = result['user_id']
            
            # Log activity
            activity_desc = f"New {data['role']} user {data['firstName']} {data['lastName']} registered"
            if data['role'] == 'organizer' and data.get('organization'):
                activity_desc += f" from {data['organization']}"
            log_activity(user_id, None, None, "user_registered", activity_desc)
            
            # Return user data with snake_case and cookie
            user_data = {
                'user_id': user_id,
                'first_name': data['firstName'],
                'last_name': data['lastName'],
                'email': data['email'],
                'role': data['role'],
                'organization': data.get('organization'),
                'phone': data.get('phone')
            }
            return create_response_with_cookie(user_data, user_id)
            
    except psycopg2.IntegrityError:
        return jsonify({"message": "Email already exists"}), 400
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"message": "Registration failed"}), 500
    
    return jsonify({"message": "Registration failed"}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    error = validate_required_fields(data, ['email', 'password'])
    if error:
        return jsonify({"message": error}), 400
    
    sql = "SELECT user_id, first_name, last_name, email, role, organization FROM users WHERE email = %s AND password = %s"
    user = execute_query(sql, (data['email'], data['password']), fetch_one=True)
    
    if user:
        user_data = dict(user)  # Keep as snake_case
        log_activity(user['user_id'], None, None, "user_login", 
                    f"User {user['first_name']} {user['last_name']} logged in successfully")
        return create_response_with_cookie(user_data, user['user_id'])
    
    return jsonify({"message": "Invalid email or password"}), 400

@app.route('/api/profile', methods=['GET'])
@require_auth
def get_profile():
    user = get_user_by_token(get_access_token())
    sql = "SELECT user_id, first_name, last_name, email, role, organization, phone, bio FROM users WHERE user_id = %s"
    profile = execute_query(sql, (user['user_id'],), fetch_one=True)
    
    if profile:
        return jsonify(dict(profile))  # Return as snake_case
    else:
        return jsonify({"message": "User not found"}), 404

@app.route('/api/validate', methods=['GET'])
def validate_email():
    email = request.args.get('email')
    if not email:
        return jsonify({"message": "Email is required"}), 400
    
    sql = "SELECT COUNT(*) as count FROM users WHERE email = %s"
    result = execute_query(sql, (email,), fetch_one=True)
    
    if result and result['count'] > 0:
        return jsonify({"message": "Email is valid"})
    return jsonify({"message": "Email is invalid"}), 400

# ==================== BUSINESS DASHBOARD ENDPOINTS ====================

@app.route('/api/events', methods=['GET'])
@require_organizer
def get_events():
    """Get all events for the logged-in organizer"""
    user = get_user_by_token(get_access_token())
    
    sql = """
        SELECT 
            e.event_id,
            e.title,
            e.category,
            e.datetime,
            e.location,
            e.general_price,
            e.vip_price,
            e.premium_price,
            e.current_registrations as attendees,
            e.status,
            COALESCE(SUM(t.price_paid), 0) as revenue,
            COUNT(CASE WHEN t.ticket_type = 'general' THEN 1 END) as general_registrations,
            COUNT(CASE WHEN t.ticket_type = 'vip' THEN 1 END) as vip_registrations,
            COUNT(CASE WHEN t.ticket_type = 'premium' THEN 1 END) as premium_registrations
        FROM events e
        LEFT JOIN tickets t ON e.event_id = t.event_id AND t.status = 'registered'
        WHERE e.organizer_id = %s
        GROUP BY e.event_id
        ORDER BY e.datetime DESC
    """
    
    events = execute_query(sql, (user['user_id'],), fetch_all=True)
    
    formatted_events = []
    for event in events:
        formatted_events.append({
            'id': event['event_id'],
            'title': event['title'],
            'category': event['category'],
            'date': event['datetime'].isoformat() if event['datetime'] else None,
            'location': event['location'],
            'price': {
                'general': float(event['general_price'] or 0),
                'vip': float(event['vip_price'] or 0),
                'premium': float(event['premium_price'] or 0)
            },
            'attendees': event['attendees'],
            'revenue': float(event['revenue']),
            'status': event['status'],
            'registrations': {
                'general': event['general_registrations'],
                'vip': event['vip_registrations'],
                'premium': event['premium_registrations']
            }
        })
    
    return jsonify({'events': formatted_events})

@app.route('/api/events/<int:event_id>', methods=['GET'])
@require_organizer
def get_event(event_id):
    """Get single event details"""
    user = get_user_by_token(get_access_token())
    
    sql = """
        SELECT * FROM events 
        WHERE event_id = %s AND organizer_id = %s
    """
    
    event = execute_query(sql, (event_id, user['user_id']), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    return jsonify(dict(event))

@app.route('/api/events', methods=['POST'])
@require_organizer
def create_event():
    """Create a new event"""
    user = get_user_by_token(get_access_token())
    data = request.get_json()
    
    # Convert snake_case from frontend
    data = convert_camel_to_snake(data)
    
    sql = """
        INSERT INTO events (
            organizer_id, title, description, category, datetime, 
            location, venue_name, general_price, vip_price, premium_price, 
            max_capacity, image_url, requirements, status
        ) VALUES (%s, %s, %s, %s::event_category, %s::timestamp, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        RETURNING event_id
    """
    
    params = (
        user['user_id'],
        data.get('title'),
        data.get('description', ''),
        data.get('category', 'other'),
        data.get('datetime'),  # Now using datetime field
        data.get('location'),
        data.get('venue') or data.get('venue_name') or data.get('location'),
        data.get('general_price', 0),
        data.get('vip_price', 0),
        data.get('premium_price', 0),
        data.get('max_capacity', 100),
        data.get('image_url'),
        data.get('requirements')
    )
    
    result = execute_query(sql, params, fetch_one=True)
    
    if result:
        log_activity(user['user_id'], result['event_id'], None, "event_created",
                    f"Created event: {data.get('title')}")
        return jsonify({"event_id": result['event_id'], "message": "Event created successfully"}), 201
    
    return jsonify({"message": "Failed to create event"}), 500

@app.route('/api/events/<int:event_id>', methods=['PUT'])
@require_organizer
def update_event(event_id):
    """Update an existing event"""
    user = get_user_by_token(get_access_token())
    data = request.get_json()
    
    # Convert snake_case from frontend
    data = convert_camel_to_snake(data)
    
    # Verify ownership
    check_sql = "SELECT * FROM events WHERE event_id = %s AND organizer_id = %s"
    event = execute_query(check_sql, (event_id, user['user_id']), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found or unauthorized"}), 404
    
    sql = """
        UPDATE events SET
            title = %s,
            description = %s,
            category = %s::event_category,
            datetime = %s::timestamp,
            location = %s,
            venue_name = %s,
            general_price = %s,
            vip_price = %s,
            premium_price = %s,
            max_capacity = %s,
            image_url = %s,
            requirements = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE event_id = %s AND organizer_id = %s
    """
    
    params = (
        data.get('title'),
        data.get('description'),
        data.get('category'),
        data.get('datetime'),
        data.get('location'),
        data.get('venue_name') or data.get('location'),
        data.get('general_price', 0),
        data.get('vip_price', 0),
        data.get('premium_price', 0),
        data.get('max_capacity', 100),
        data.get('image_url'),
        data.get('requirements'),
        event_id,
        user['user_id']
    )
    
    result = execute_query(sql, params)
    
    if result:
        log_activity(user['user_id'], event_id, None, "event_updated",
                    f"Updated event: {data.get('title')}")
        return jsonify({"message": "Event updated successfully"})
    
    return jsonify({"message": "Failed to update event"}), 500

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@require_organizer
def delete_event(event_id):
    """Delete an event and refund all tickets"""
    user = get_user_by_token(get_access_token())
    
    # Verify ownership
    check_sql = "SELECT title FROM events WHERE event_id = %s AND organizer_id = %s"
    event = execute_query(check_sql, (event_id, user['user_id']), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found or unauthorized"}), 404
    
    try:
        # Start a transaction to ensure both operations succeed or fail together
        
        # 1. Update all tickets for this event to 'refunded' status
        refund_sql = """
            UPDATE tickets 
            SET status = 'refunded' 
            WHERE event_id = %s AND status IN ('registered', 'pending')
        """
        refund_result = execute_query(refund_sql, (event_id,))
        
        # 2. Get count of refunded tickets for logging
        count_sql = """
            SELECT COUNT(*) as count 
            FROM tickets 
            WHERE event_id = %s AND status = 'refunded'
        """
        refund_count = execute_query(count_sql, (event_id,), fetch_one=True)
        
        # 3. Soft delete by updating event status to 'cancelled'
        cancel_sql = "UPDATE events SET status = 'cancelled' WHERE event_id = %s AND organizer_id = %s"
        cancel_result = execute_query(cancel_sql, (event_id, user['user_id']))
        
        if cancel_result:
            # Log the activity with refund information
            log_activity(
                user['user_id'], 
                event_id, 
                None, 
                "event_cancelled",
                f"Cancelled event: {event['title']} and refunded {refund_count['count']} tickets"
            )
            
            # Optionally, log individual refund activities for each affected user
            refunded_users_sql = """
                SELECT DISTINCT user_id, COUNT(*) as ticket_count 
                FROM tickets 
                WHERE event_id = %s AND status = 'refunded'
                GROUP BY user_id
            """
            refunded_users = execute_query(refunded_users_sql, (event_id,), fetch_all=True)
            
            for refunded_user in refunded_users:
                log_activity(
                    refunded_user['user_id'],
                    event_id,
                    None,
                    "ticket_refunded",
                    f"Your {refunded_user['ticket_count']} ticket(s) for '{event['title']}' have been refunded due to event cancellation"
                )
            
            return jsonify({
                "message": "Event cancelled successfully",
                "tickets_refunded": refund_count['count']
            })
            
    except Exception as e:
        # If any error occurs, the transaction should be rolled back
        # (assuming your execute_query handles transactions properly)
        return jsonify({"message": f"Failed to delete event: {str(e)}"}), 500
    
    return jsonify({"message": "Failed to delete event"}), 500

@app.route('/api/events/<int:event_id>/report', methods=['GET'])
@require_organizer
def get_event_report(event_id):
    """Get detailed report for an event"""
    user = get_user_by_token(get_access_token())
    
    # Verify ownership
    check_sql = "SELECT * FROM events WHERE event_id = %s AND organizer_id = %s"
    event = execute_query(check_sql, (event_id, user['user_id']), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found or unauthorized"}), 404
    
    # Get ticket statistics
    stats_sql = """
        SELECT 
            ticket_type,
            COUNT(*) as count,
            SUM(price_paid) as revenue
        FROM tickets
        WHERE event_id = %s AND status = 'registered'
        GROUP BY ticket_type
    """
    
    stats = execute_query(stats_sql, (event_id,), fetch_all=True)
    
    report = {
        'event': dict(event),
        'ticket_stats': [dict(stat) for stat in stats] if stats else []
    }
    
    return jsonify(report)

@app.route('/api/events/<int:event_id>/reminder', methods=['POST'])
@require_organizer
def send_event_reminder(event_id):
    """Send reminder to all event attendees"""
    user = get_user_by_token(get_access_token())
    
    # Verify ownership
    check_sql = "SELECT title FROM events WHERE event_id = %s AND organizer_id = %s"
    event = execute_query(check_sql, (event_id, user['user_id']), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found or unauthorized"}), 404
    
    # Get all attendees for this event
    attendees_sql = """SELECT DISTINCT t.user_id, t.ticket_id 
                       FROM tickets t 
                       WHERE t.event_id = %s AND t.status = 'registered'"""
    attendees = execute_query(attendees_sql, (event_id,), fetch_all=True)
    
    attendee_count = len(attendees) if attendees else 0
    
    # Log activity for each attendee
    for attendee in attendees:
        log_activity(attendee['user_id'], event_id, attendee['ticket_id'], "reminder_received",
                    f"Received reminder for event: {event['title']}")
    
    # Log activity for organizer
    log_activity(user['user_id'], event_id, None, "reminder_sent",
                f"Sent reminder to {attendee_count} attendees for {event['title']}")
    
    return jsonify({"message": f"Reminder sent to {attendee_count} attendees"})

@app.route('/api/registrations/<int:registration_id>/accept', methods=['PUT'])
@require_organizer
def accept_registration(registration_id):
    """Accept a ticket registration"""
    user = get_user_by_token(get_access_token())
    
    # Verify ownership
    check_sql = """
        SELECT t.*, e.title as event_title 
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.ticket_id = %s AND e.organizer_id = %s
    """
    ticket = execute_query(check_sql, (registration_id, user['user_id']), fetch_one=True)
    
    if not ticket:
        return jsonify({"message": "Registration not found or unauthorized"}), 404
    
    # Update status from pending to registered
    sql = "UPDATE tickets SET status = 'registered' WHERE ticket_id = %s"
    result = execute_query(sql, (registration_id,))
    
    if result:
        log_activity(user['user_id'], ticket['event_id'], registration_id, "registration_accepted",
                    f"Accepted registration for {ticket['event_title']}")
        return jsonify({"message": "Registration accepted"})
    
    return jsonify({"message": "Failed to accept registration"}), 500

@app.route('/api/registrations/<int:registration_id>/reject', methods=['PUT'])
@require_organizer
def reject_registration(registration_id):
    """Reject a ticket registration"""
    user = get_user_by_token(get_access_token())
    
    # Verify ownership
    check_sql = """
        SELECT t.*, e.title as event_title 
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        WHERE t.ticket_id = %s AND e.organizer_id = %s
    """
    ticket = execute_query(check_sql, (registration_id, user['user_id']), fetch_one=True)
    
    if not ticket:
        return jsonify({"message": "Registration not found or unauthorized"}), 404
    
    # Update status from pending to rejected
    sql = "UPDATE tickets SET status = 'rejected' WHERE ticket_id = %s"
    result = execute_query(sql, (registration_id,))
    
    if result:
        # Update event registration count if the ticket was previously registered
        if ticket['status'] == 'registered':
            execute_query("UPDATE events SET current_registrations = current_registrations - 1 WHERE event_id = %s", 
                         (ticket['event_id'],))
        
        log_activity(user['user_id'], ticket['event_id'], registration_id, "registration_rejected",
                    f"Rejected registration for {ticket['event_title']}")
        return jsonify({"message": "Registration rejected"})
    
    return jsonify({"message": "Failed to reject registration"}), 500

@app.route('/api/registrations', methods=['GET'])
@require_organizer
def get_registrations():
    """Get recent ticket registrations for organizer's events"""
    user = get_user_by_token(get_access_token())
    
    limit = request.args.get('limit', 50, type=int)
    
    sql = """
        SELECT 
            t.ticket_id as id,
            COALESCE(t.customer_name, u.first_name || ' ' || u.last_name) as customer_name,
            COALESCE(t.customer_email, u.email) as customer_email,
            e.title as event_title,
            e.event_id,
            t.ticket_type,
            COALESCE(t.quantity, 1) as quantity,
            t.price_paid as total_amount,
            COALESCE(t.purchase_date, t.created_at) as purchase_date,
            t.status
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        JOIN users u ON t.user_id = u.user_id
        WHERE e.organizer_id = %s
        ORDER BY t.created_at DESC
        LIMIT %s
    """
    
    registrations = execute_query(sql, (user['user_id'], limit), fetch_all=True)
    
    formatted_registrations = []
    for reg in registrations:
        formatted_registrations.append({
            'id': reg['id'],
            'customer_name': reg['customer_name'],
            'customer_email': reg['customer_email'],
            'event_title': reg['event_title'],
            'event_id': reg['event_id'],
            'ticket_type': reg['ticket_type'],
            'quantity': reg['quantity'],
            'total_amount': float(reg['total_amount']),
            'purchase_date': reg['purchase_date'].isoformat() if reg['purchase_date'] else None,
            'status': reg['status']  # Use the actual status from DB
        })
    
    return jsonify({'registrations': formatted_registrations})

@app.route('/api/notifications', methods=['GET'])
# @require_organizer
def get_notifications():
    """Get notifications for the user"""
    user = get_user_by_token(get_access_token())
    
    if user['role'] == 'organizer':
        # Organizer notifications - events they organize
        sql = """
            SELECT 
                a.activity_id as id,
                CASE 
                    WHEN a.activity_type = 'ticket_booked' THEN 'New Registration'
                    WHEN a.activity_type = 'registration_cancelled' THEN 'Registration Cancelled'
                    WHEN a.activity_type = 'event_updated' THEN 'Event Update'
                    ELSE 'Event Update'
                END as title,
                a.description as message,
                CASE 
                    WHEN a.created_at > NOW() - INTERVAL '1 hour' THEN 
                        EXTRACT(MINUTE FROM NOW() - a.created_at) || ' minutes ago'
                    WHEN a.created_at > NOW() - INTERVAL '24 hours' THEN 
                        EXTRACT(HOUR FROM NOW() - a.created_at) || ' hours ago'
                    ELSE 
                        EXTRACT(DAY FROM NOW() - a.created_at) || ' days ago'
                END as time,
                CASE 
                    WHEN a.activity_type = 'ticket_booked' THEN 'registration'
                    WHEN a.activity_type = 'registration_cancelled' THEN 'cancellation'
                    ELSE 'update'
                END as type,
                a.created_at > NOW() - INTERVAL '2 hours' as unread
            FROM activity a
            JOIN events e ON a.event_id = e.event_id
            WHERE e.organizer_id = %s
            ORDER BY a.created_at DESC
            LIMIT 20
        """
        activities = execute_query(sql, (user['user_id'],), fetch_all=True)
    else:
        # Regular user notifications - activities related to their own actions
        sql = """
            SELECT 
                a.activity_id as id,
                CASE 
                    WHEN a.activity_type = 'ticket_booked' THEN 'Ticket Booked'
                    WHEN a.activity_type = 'registration_accepted' THEN 'Registration Accepted'
                    WHEN a.activity_type = 'registration_rejected' THEN 'Registration Rejected'
                    WHEN a.activity_type = 'reminder_received' THEN 'Event Reminder'
                    ELSE 'Account Activity'
                END as title,
                a.description as message,
                CASE 
                    WHEN a.created_at > NOW() - INTERVAL '1 hour' THEN 
                        EXTRACT(MINUTE FROM NOW() - a.created_at) || ' minutes ago'
                    WHEN a.created_at > NOW() - INTERVAL '24 hours' THEN 
                        EXTRACT(HOUR FROM NOW() - a.created_at) || ' hours ago'
                    ELSE 
                        EXTRACT(DAY FROM NOW() - a.created_at) || ' days ago'
                END as time,
                CASE 
                    WHEN a.activity_type = 'ticket_booked' THEN 'booking'
                    WHEN a.activity_type = 'registration_accepted' THEN 'confirmation'
                    WHEN a.activity_type = 'registration_rejected' THEN 'rejection'
                    WHEN a.activity_type = 'reminder_received' THEN 'reminder'
                    ELSE 'activity'
                END as type,
                a.created_at > NOW() - INTERVAL '2 hours' as unread
            FROM activity a
            WHERE a.user_id = %s
            ORDER BY a.created_at DESC
            LIMIT 20
        """
        activities = execute_query(sql, (user['user_id'],), fetch_all=True)
    
    notifications = []
    for activity in activities:
        notifications.append({
            'id': activity['id'],
            'title': activity['title'],
            'message': activity['message'],
            'time': activity['time'],
            'type': activity['type'],
            'unread': activity['unread']
        })
    
    return jsonify({'notifications': notifications})

@app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
@require_organizer
def mark_notification_read(notification_id):
    """Mark notification as read"""
    # In a real system, this would update a notifications table
    return jsonify({"message": "Notification marked as read"})

@app.route('/api/dashboard/stats', methods=['GET'])
@require_organizer
def get_dashboard_stats():
    """Get dashboard statistics for organizer"""
    user = get_user_by_token(get_access_token())
    
    # Get total events
    events_sql = "SELECT COUNT(*) as count FROM events WHERE organizer_id = %s"
    events_result = execute_query(events_sql, (user['user_id'],), fetch_one=True)
    
    # Get total attendees and revenue
    attendees_sql = """
        SELECT 
            COUNT(DISTINCT t.user_id) as total_attendees,
            COALESCE(SUM(t.price_paid), 0) as total_revenue
        FROM tickets t
        JOIN events e ON t.event_id = e.event_id
        WHERE e.organizer_id = %s AND t.status = 'registered'
    """
    attendees_result = execute_query(attendees_sql, (user['user_id'],), fetch_one=True)
    
    # Get active events (upcoming events)
    active_sql = """
        SELECT COUNT(*) as count 
        FROM events 
        WHERE organizer_id = %s AND status = 'active' AND datetime > NOW()
    """
    active_result = execute_query(active_sql, (user['user_id'],), fetch_one=True)
    
    stats = {
        'total_events': events_result['count'] if events_result else 0,
        'total_attendees': attendees_result['total_attendees'] if attendees_result else 0,
        'total_revenue': float(attendees_result['total_revenue']) if attendees_result else 0,
        'active_events': active_result['count'] if active_result else 0
    }
    
    return jsonify(stats)

@app.route('/api/auth/logout', methods=['POST']) 
@require_auth
def logout():
    """Logout user"""
    user = get_user_by_token(get_access_token())
    
    if user:
        log_activity(user['user_id'], None, None, "user_logout",
                    f"User {user['first_name']} {user['last_name']} logged out")
    
    response = make_response(jsonify({"message": "Logged out successfully"}))
    response.set_cookie('accessToken', '', expires=0)
    
    return response

# ==================== CUSTOMER ENDPOINTS ====================

@app.route('/api/customer-events', methods=['GET'])
def get_public_events():
    """Get all active events for customers"""
    
    # Check if user is authenticated to determine which endpoint to use
    user = get_user_by_token(get_access_token())
    if user and user.get('role') == 'organizer':
        # If organizer, redirect to organizer events endpoint
        return get_events()
    
    # Build dynamic query based on filters
    base_sql = """SELECT e.*, u.first_name as organizer_first_name, u.last_name as organizer_last_name, 
                  u.organization as organizer_organization FROM events e 
                  JOIN users u ON e.organizer_id = u.user_id WHERE e.status = 'active'"""
    
    params = []
    filters = []
    
    if request.args.get('category'):
        filters.append("e.category = %s::event_category")
        params.append(request.args.get('category'))
    
    if request.args.get('location'):
        filters.append("e.location ILIKE %s")
        params.append(f"%{request.args.get('location')}%")
    
    if request.args.get('organizer'):
        organizer = request.args.get('organizer')
        filters.append("(u.organization ILIKE %s OR u.first_name ILIKE %s OR u.last_name ILIKE %s)")
        params.extend([f"%{organizer}%", f"%{organizer}%", f"%{organizer}%"])
    
    sql = base_sql + (" AND " + " AND ".join(filters) if filters else "") + " ORDER BY e.datetime ASC"
    events = execute_query(sql, params, fetch_all=True)
    
    # Format events with organizer name
    formatted_events = []
    for event in events:
        event_dict = dict(event)
        organizer_name = event['organizer_organization'] or f"{event['organizer_first_name']} {event['organizer_last_name']}"
        event_dict['organizer_name'] = organizer_name
        # Remove the separate organizer fields
        del event_dict['organizer_first_name']
        del event_dict['organizer_last_name']
        del event_dict['organizer_organization']
        formatted_events.append(event_dict)
    
    return jsonify(formatted_events)

@app.route('/api/tickets', methods=['POST'])
@require_auth
def book_ticket():
    """Book a ticket for an event"""
    user = get_user_by_token(get_access_token())
    data = request.get_json()
    
    if not data.get('event_id'):
        return jsonify({"message": "Event ID is required"}), 400
    
    event_id = data['event_id']
    ticket_type = data.get('ticket_type', 'general')
    
    # Get event details
    event_sql = """SELECT title, general_price, vip_price, premium_price, max_capacity,
                   current_registrations FROM events WHERE event_id = %s AND status = 'active'"""
    event = execute_query(event_sql, (event_id,), fetch_one=True)
    
    if not event:
        return jsonify({"message": "Event not found or not available"}), 400
    
    if event['current_registrations'] >= event['max_capacity']:
        return jsonify({"message": "Event is fully booked"}), 400
    
    # Get price based on ticket type
    price_map = {'vip': 'vip_price', 'premium': 'premium_price', 'general': 'general_price'}
    price = event[price_map.get(ticket_type, 'general_price')]
    
    # Check for duplicate booking
    duplicate_sql = "SELECT COUNT(*) as count FROM tickets WHERE event_id = %s AND user_id = %s AND ticket_type = %s::ticket_type"
    duplicate = execute_query(duplicate_sql, (event_id, user['user_id'], ticket_type), fetch_one=True)
    
    if duplicate and duplicate['count'] > 0:
        return jsonify({"message": f"You already have a {ticket_type} ticket for this event"}), 400
    
    # Create ticket
    booking_ref = generate_booking_reference()
    ticket_sql = """INSERT INTO tickets (event_id, user_id, ticket_type, price_paid, booking_reference,
                    special_requests, customer_name, customer_email, status) 
                    VALUES (%s, %s, %s::ticket_type, %s, %s, %s, %s, %s, 'pending')
                    RETURNING ticket_id"""
    
    customer_name = f"{user['first_name']} {user['last_name']}"
    ticket = execute_query(ticket_sql, (event_id, user['user_id'], ticket_type, price,
                          booking_ref, data.get('special_requests'), customer_name, user['email']), fetch_one=True)
    
    if ticket:
        # Update event registration count
        execute_query("UPDATE events SET current_registrations = current_registrations + 1 WHERE event_id = %s", (event_id,))
        
        # Log activity
        log_activity(user['user_id'], event_id, ticket['ticket_id'], "ticket_booked",
                    f"Booked {ticket_type} ticket for \"{event['title']}\" - ${price:.2f}")
        
        response = {
            "ticket_id": ticket['ticket_id'],
            "booking_reference": booking_ref,
            "event_title": event['title'],
            "ticket_type": ticket_type,
            "price": float(price),
            "message": "Ticket booked successfully"
        }
        return jsonify(response), 201
    
    return jsonify({"message": "Failed to book ticket"}), 500

@app.route('/api/tickets', methods=['GET'])
@require_auth
def get_user_tickets():
    """Get all tickets for the logged-in user"""
    user = get_user_by_token(get_access_token())
    
    sql = """SELECT t.*, e.title as event_title, e.datetime, e.location, e.venue_name 
             FROM tickets t JOIN events e ON t.event_id = e.event_id 
             WHERE t.user_id = %s ORDER BY e.datetime ASC"""
    
    tickets = execute_query(sql, (user['user_id'],), fetch_all=True)
    formatted_tickets = [dict(ticket) for ticket in tickets]  # Keep as snake_case
    
    return jsonify(formatted_tickets)

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get statistics for the logged-in user"""
    user = get_user_by_token(get_access_token())
    stats = {}
    
    if user['role'] == 'organizer':
        # Organizer stats
        event_count = execute_query("SELECT COUNT(*) as count FROM events WHERE organizer_id = %s", 
                                  (user['user_id'],), fetch_one=True)
        stats['total_events'] = event_count['count'] if event_count else 0
        
        ticket_count = execute_query("""SELECT COUNT(*) as count FROM tickets t 
                                      JOIN events e ON t.event_id = e.event_id 
                                      WHERE e.organizer_id = %s""", 
                                   (user['user_id'],), fetch_one=True)
        stats['total_tickets_sold'] = ticket_count['count'] if ticket_count else 0
        
        revenue = execute_query("""SELECT COALESCE(SUM(t.price_paid), 0) as revenue 
                                FROM tickets t JOIN events e ON t.event_id = e.event_id 
                                WHERE e.organizer_id = %s AND t.status = 'registered'""", 
                              (user['user_id'],), fetch_one=True)
        stats['total_revenue'] = float(revenue['revenue']) if revenue else 0
        
    elif user['role'] == 'attendee':
        # Attendee stats
        ticket_count = execute_query("SELECT COUNT(*) as count FROM tickets WHERE user_id = %s", 
                                   (user['user_id'],), fetch_one=True)
        stats['total_tickets'] = ticket_count['count'] if ticket_count else 0
        
        upcoming = execute_query("""SELECT COUNT(*) as count FROM tickets t 
                                  JOIN events e ON t.event_id = e.event_id 
                                  WHERE t.user_id = %s AND e.datetime > CURRENT_TIMESTAMP""", 
                               (user['user_id'],), fetch_one=True)
        stats['upcoming_events'] = upcoming['count'] if upcoming else 0
        
        spent = execute_query("""SELECT COALESCE(SUM(price_paid), 0) as spent FROM tickets 
                              WHERE user_id = %s AND status = 'registered'""", 
                            (user['user_id'],), fetch_one=True)
        stats['total_spent'] = float(spent['spent']) if spent else 0
    
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5174)