import json
import traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('food_donation.db')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT UNIQUE NOT NULL,
                 password TEXT NOT NULL,
                 role TEXT NOT NULL,
                 location TEXT,
                 phone TEXT,
                 profile_pic TEXT,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS listings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 farmer_id INTEGER NOT NULL,
                 produce_type TEXT NOT NULL,
                 quantity REAL NOT NULL,
                 price REAL DEFAULT 0,
                 description TEXT,
                 harvest_date TEXT,
                 best_before TEXT,
                 organic BOOLEAN DEFAULT 0,
                 images TEXT,
                 status TEXT DEFAULT 'active',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (farmer_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 listing_id INTEGER NOT NULL,
                 buyer_id INTEGER,
                 foodbank_id INTEGER,
                 quantity REAL NOT NULL,
                 purpose TEXT,
                 status TEXT DEFAULT 'pending',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (listing_id) REFERENCES listings(id),
                 FOREIGN KEY (buyer_id) REFERENCES users(id),
                 FOREIGN KEY (foodbank_id) REFERENCES users(id))''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 sender_id INTEGER NOT NULL,
                 receiver_id INTEGER NOT NULL,
                 content TEXT NOT NULL,
                 read BOOLEAN DEFAULT 0,
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (sender_id) REFERENCES users(id),
                 FOREIGN KEY (receiver_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()

init_db()

# Helper functions
def get_db():
    conn = sqlite3.connect('food_donation.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_user(email, password):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                       (email, password)).fetchone()
    conn.close()
    return dict(user) if user else None

# API Endpoints
@app.route('/')
def home():
    return "API Ready for Render"
    
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = validate_user(data['email'], data['password'])
    
    if user and user['role'].lower() == data['role'].lower():
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Invalid credentials or role"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db()
    
    try:
        profile_pic = data.get('profile_pic', None)
        
        c = conn.cursor()
        c.execute('''INSERT INTO users 
                     (name, email, password, role, location, phone, profile_pic)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (data['name'], data['email'], data['password'], data['role'],
                  data.get('location'), data.get('phone'), profile_pic))
        
        conn.commit()
        user_id = c.lastrowid
        user = dict(conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone())
        conn.close()
        return jsonify({"success": True, "user": user})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"})

@app.route('/listings', methods=['GET', 'POST'])
def listings():
    if 'images[]' in request.files:
        images = request.files.getlist('images[]')
        image_data = []
        for img in images:
            if img.filename != '':
                try:
                    # Validate it's an image
                    Image.open(img.stream)
                    img.stream.seek(0)
                    image_data.append(base64.b64encode(img.read()).decode('utf-8'))
                except:
                    continue
    else:
        image_data = []

    if request.method == 'POST':
        data = request.json
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''INSERT INTO listings 
                     (farmer_id, produce_type, quantity, price, description, 
                      harvest_date, best_before, organic, images)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (data['farmer_id'], data['produce_type'], data['quantity'],
                  data.get('price', 0), data.get('description'),
                  data['harvest_date'], data['best_before'],
                  data.get('organic', False),
                  json.dumps(data.get('images', []))))
        
        conn.commit()
        listing_id = c.lastrowid
        listing = dict(conn.execute('SELECT * FROM listings WHERE id = ?', (listing_id,)).fetchone())
        conn.close()
        return jsonify({"success": True, "listing": listing})
    
    # GET method
    conn = get_db()
    listings = conn.execute('SELECT * FROM listings WHERE status = "active"').fetchall()
    conn.close()
    return jsonify([dict(row) for row in listings])

@app.route('/listings/farmer/<int:farmer_id>', methods=['GET'])
def farmer_listings(farmer_id):
    conn = get_db()
    listings = conn.execute('SELECT * FROM listings WHERE farmer_id = ?', (farmer_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in listings])

@app.route('/listings/<int:listing_id>', methods=['DELETE'])
def delete_listing(listing_id):
    conn = get_db()
    conn.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/listings/active', methods=['GET'])
def active_listings():
    conn = get_db()
    # Get listings with farmer info for the buyer view
    listings = conn.execute('''
        SELECT l.*, u.name as farmer_name, u.location 
        FROM listings l
        JOIN users u ON l.farmer_id = u.id
        WHERE l.status = "active"
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in listings])

# Add this endpoint for food bank donations
@app.route('/listings/donations', methods=['GET'])
def donation_listings():
    conn = get_db()
    # Get free listings (price = 0) for food banks
    listings = conn.execute('''
        SELECT l.*, u.name as farmer_name, u.location 
        FROM listings l
        JOIN users u ON l.farmer_id = u.id
        WHERE l.status = "active" AND l.price = 0
    ''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in listings])

@app.route('/listings/<int:listing_id>/status', methods=['PUT'])
def update_listing_status(listing_id):
    data = request.json
    conn = get_db()
    try:
        conn.execute('UPDATE listings SET status = ? WHERE id = ?',
                    (data['status'], listing_id))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/requests', methods=['POST'])
def create_request():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''INSERT INTO requests 
                 (listing_id, buyer_id, foodbank_id, quantity, purpose, status)
                 VALUES (?, ?, ?, ?, ?, ?)''',
             (data['listing_id'], data.get('buyer_id'), data.get('foodbank_id'),
              data['quantity'], data.get('purpose'), data.get('status', 'pending')))
    
    conn.commit()
    request_id = c.lastrowid
    req = dict(conn.execute('SELECT * FROM requests WHERE id = ?', (request_id,)).fetchone())
    conn.close()
    return jsonify({"success": True, "request": req})

# Get requests for a farmer (all requests for their listings)
@app.route('/requests/farmer/<int:farmer_id>', methods=['GET'])
def farmer_requests(farmer_id):
    conn = get_db()
    requests = conn.execute('''
        SELECT r.*, l.produce_type, 
               COALESCE(u1.name, u2.name) as requester_name,
               COALESCE(r.buyer_id, r.foodbank_id) as requester_id
        FROM requests r
        JOIN listings l ON r.listing_id = l.id
        LEFT JOIN users u1 ON r.buyer_id = u1.id
        LEFT JOIN users u2 ON r.foodbank_id = u2.id
        WHERE l.farmer_id = ?
    ''', (farmer_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in requests])

# Get requests made by a buyer
@app.route('/requests/buyer/<int:buyer_id>', methods=['GET'])
def buyer_requests(buyer_id):
    conn = get_db()
    requests = conn.execute('''
        SELECT r.*, l.produce_type, u.name as farmer_name
        FROM requests r
        JOIN listings l ON r.listing_id = l.id
        JOIN users u ON l.farmer_id = u.id
        WHERE r.buyer_id = ?
    ''', (buyer_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in requests])

# Get requests made by a food bank
@app.route('/requests/foodbank/<int:foodbank_id>', methods=['GET'])
def foodbank_requests(foodbank_id):
    conn = get_db()
    requests = conn.execute('''
        SELECT r.*, l.produce_type, u.name as farmer_name
        FROM requests r
        JOIN listings l ON r.listing_id = l.id
        JOIN users u ON l.farmer_id = u.id
        WHERE r.foodbank_id = ?
    ''', (foodbank_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in requests])

# Update request status
@app.route('/requests/<int:request_id>', methods=['PUT'])
def update_request(request_id):
    conn = None
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        required_fields = ['status', 'quantity', 'listing_id', 'farmer_id']
        if not all(field in data for field in required_fields):
            return jsonify({
                "success": False,
                "error": f"Missing required fields. Need: {', '.join(required_fields)}"
            }), 400

        conn = get_db()
        c = conn.cursor()

        # Verify request exists and belongs to this farmer
        request_data = c.execute('''
            SELECT r.*, l.farmer_id as listing_farmer_id, l.quantity as available_quantity
            FROM requests r
            JOIN listings l ON r.listing_id = l.id
            WHERE r.id = ?
        ''', (request_id,)).fetchone()

        if not request_data:
            return jsonify({"success": False, "error": "Request not found"}), 404

        request_data = dict(request_data)
        
        # Authorization check
        if int(request_data['listing_farmer_id']) != int(data['farmer_id']):
            return jsonify({
                "success": False,
                "error": "Unauthorized - you don't own this listing"
            }), 403

        # Convert quantities to float for comparison
        requested_qty = float(data['quantity'])
        available_qty = float(request_data['available_quantity'])

        # Quantity validation
        if data['status'] == 'approved' and requested_qty > available_qty:
            return jsonify({
                "success": False,
                "error": f"Requested quantity ({requested_qty}) exceeds available quantity ({available_qty})"
            }), 400

        # Update request status
        c.execute('''
            UPDATE requests
            SET status = ?
            WHERE id = ?
        ''', (data['status'], request_id))

        # Update listing quantity if approved
        if data['status'] == 'approved':
            c.execute('''
                UPDATE listings
                SET quantity = quantity - ?
                WHERE id = ?
            ''', (requested_qty, data['listing_id']))

        conn.commit()
        return jsonify({"success": True, "message": "Request updated successfully"})

    except Exception as e:
        if conn:
            conn.rollback()
        app.logger.error(f"Error updating request: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
        
    finally:
        if conn:
            conn.close()

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.json
    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (?, ?, ?)
        ''', (data['sender_id'], data['receiver_id'], data['content']))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/messages/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_messages(user1_id, user2_id):
    conn = get_db()
    try:
        messages = conn.execute('''
            SELECT m.*, u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE (sender_id = ? AND receiver_id = ?)
               OR (sender_id = ? AND receiver_id = ?)
            ORDER BY created_at
        ''', (user1_id, user2_id, user2_id, user1_id)).fetchall()
        
        # Mark received messages as read
        conn.execute('''
            UPDATE messages SET read = 1
            WHERE receiver_id = ? AND sender_id = ? AND read = 0
        ''', (user1_id, user2_id))
        conn.commit()
        
        return jsonify([dict(msg) for msg in messages])
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    conn = get_db()
    try:
        conversations = conn.execute('''
            SELECT 
                CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as partner_id,
                u.name as partner_name,
                MAX(m.created_at) as last_message_time,
                SUM(CASE WHEN receiver_id = ? AND read = 0 THEN 1 ELSE 0 END) as unread_count
            FROM messages m
            JOIN users u ON CASE WHEN m.sender_id = ? THEN m.receiver_id ELSE m.sender_id END = u.id
            WHERE sender_id = ? OR receiver_id = ?
            GROUP BY partner_id, partner_name
            ORDER BY last_message_time DESC
        ''', (user_id, user_id, user_id, user_id, user_id)).fetchall()
        
        return jsonify([dict(conv) for conv in conversations])
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/update_profile', methods=['PUT'])
def update_profile():
    data = request.json
    conn = get_db()
    try:
        conn.execute('''
            UPDATE users 
            SET name = ?, location = ?, phone = ?
            WHERE id = ?
        ''', (data['name'], data['location'], data['phone'], data['user_id']))
        conn.commit()
        
        # Return updated user data
        user = conn.execute('SELECT * FROM users WHERE id = ?', (data['user_id'],)).fetchone()
        return jsonify({"success": True, "user": dict(user)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    conn = get_db()
    try:
        # Verify current password
        user = conn.execute('SELECT * FROM users WHERE id = ? AND password = ?',
                          (data['user_id'], data['current_password'])).fetchone()
        if not user:
            return jsonify({"success": False, "message": "Current password is incorrect"}), 401
        
        # Update password
        conn.execute('UPDATE users SET password = ? WHERE id = ?',
                   (data['new_password'], data['user_id']))
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()

@app.route('/update_profile_pic', methods=['PUT'])
def update_profile_pic():
    conn = None
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'profile_pic' not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Verify user exists first
        user = cursor.execute('SELECT id FROM users WHERE id = ?', (data['user_id'],)).fetchone()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Update profile picture
        cursor.execute('''
            UPDATE users 
            SET profile_pic = ?
            WHERE id = ?
        ''', (data['profile_pic'], data['user_id']))
        
        conn.commit()
        
        # Get updated user data
        updated_user = cursor.execute('''
            SELECT id, name, email, role, location, phone, profile_pic
            FROM users 
            WHERE id = ?
        ''', (data['user_id'],)).fetchone()
        
        return jsonify({
            "success": True,
            "user": dict(updated_user) if updated_user else None
        })
        
    except Exception as e:
        app.logger.error(f"Error updating profile pic: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
    finally:
        if conn:
            conn.close()

@app.route('/health', methods=['GET'])
def health_check():
    try:
        conn = get_db()
        conn.execute("SELECT 1")  # Simple DB check
        conn.close()
        return jsonify({
            "status": "healthy",
            "database": "connected"
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
    
@app.route('/debug/request/<int:request_id>')
def debug_request(request_id):
    conn = get_db()
    req = conn.execute('SELECT * FROM requests WHERE id = ?', (request_id,)).fetchone()
    listing = conn.execute('SELECT * FROM listings WHERE id = ?', (req['listing_id'],)).fetchone() if req else None
    conn.close()
    return jsonify({
        "request": dict(req) if req else None,
        "listing": dict(listing) if listing else None
    })

if __name__ == '__main__':
    app.run(app.run(host='0.0.0.0', port=10000))
