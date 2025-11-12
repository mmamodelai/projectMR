#!/usr/bin/env python3
"""
SMSConductor REST API Server
Provides HTTP endpoints for n8n.io integration

Usage:
    python api_server.py
    
Endpoints:
    GET  /api/messages/unread     - Get unread incoming messages
    POST /api/messages/mark-read  - Mark message as read
    POST /api/messages/send       - Queue message for sending
    GET  /api/status              - Get system status
    GET  /api/health              - Health check
"""

from flask import Flask, request, jsonify
import sqlite3
import json
import os
from datetime import datetime
import logging
import hashlib

app = Flask(__name__)

# Load configuration
def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file 'config.json' not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in configuration file: {e}")
        return None

config = load_config()
if not config:
    exit(1)

DB_PATH = config['database']['path']

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - API - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def calculate_message_hash(phone_number, content):
    """Calculate hash for duplicate detection"""
    data = f"{phone_number}|{content}".encode('utf-8')
    return hashlib.sha256(data).hexdigest()[:16]

def split_long_message(content, max_length=150):
    """
    Split long messages into multiple SMS segments
    
    Args:
        content: The message content to split
        max_length: Maximum characters per segment (default 150 for safety)
    
    Returns:
        List of message segments
    """
    if len(content) <= max_length:
        return [content]
    
    segments = []
    words = content.split()
    current_segment = ""
    
    for word in words:
        # Check if adding this word would exceed the limit
        test_segment = current_segment + (" " if current_segment else "") + word
        
        if len(test_segment) <= max_length:
            current_segment = test_segment
        else:
            # Current segment is full, start a new one
            if current_segment:
                segments.append(current_segment)
            current_segment = word
    
    # Add the last segment if it has content
    if current_segment:
        segments.append(current_segment)
    
    return segments

@app.route('/api/messages/unread', methods=['GET'])
def get_unread_messages():
    """Get all unread incoming messages"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, phone_number, content, timestamp, modem_timestamp, message_hash
                FROM messages 
                WHERE status = 'unread' AND direction = 'inbound'
                ORDER BY timestamp DESC
            """)
            messages = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Retrieved {len(messages)} unread messages")
            
            return jsonify({
                'success': True,
                'count': len(messages),
                'messages': messages,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting unread messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/messages/send', methods=['POST'])
def queue_message():
    """Queue a message for sending (with automatic splitting for long messages)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'JSON data required'}), 400
        
        phone_number = data.get('phone_number')
        message = data.get('message')
        
        if not phone_number or not message:
            return jsonify({'success': False, 'error': 'phone_number and message required'}), 400
        
        # Split long messages into segments
        segments = split_long_message(message)
        
        if len(segments) > 1:
            logger.info(f"Message split into {len(segments)} segments for {phone_number[:7]}****")
        
        message_ids = []
        timestamp = datetime.now().isoformat()
        queued_segments = 0
        
        with sqlite3.connect(DB_PATH) as conn:
            for i, segment in enumerate(segments):
                # Calculate hash for each segment
                msg_hash = calculate_message_hash(phone_number, segment)
                
                # Check for duplicates in last 24 hours
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE message_hash = ? 
                    AND timestamp > datetime('now', '-1 day')
                """, (msg_hash,))
                duplicate_count = cursor.fetchone()[0]
                
                if duplicate_count > 0:
                    logger.warning(f"Duplicate segment {i+1}/{len(segments)} detected: {phone_number[:7]}****")
                    continue
                
                # Use segment content as-is (no numbering)
                segment_content = segment
                
                conn.execute("""
                    INSERT INTO messages 
                    (phone_number, content, timestamp, status, direction, message_hash)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (phone_number, segment_content, timestamp, 'queued', 'outbound', msg_hash))
                conn.commit()
                
                cursor = conn.execute("SELECT last_insert_rowid()")
                msg_id = cursor.fetchone()[0]
                message_ids.append(msg_id)
                queued_segments += 1
                
                logger.info(f"Queued segment {queued_segments}/{len(segments)} (ID: {msg_id}) for {phone_number[:7]}****")
        
        if not message_ids:
            return jsonify({
                'success': False, 
                'error': 'All message segments were duplicates',
                'duplicate': True
            }), 409
        
        return jsonify({
            'success': True,
            'message_ids': message_ids,
            'segments': queued_segments,
            'total_segments': len(segments),
            'status': 'queued',
            'timestamp': timestamp
        })
    except Exception as e:
        logger.error(f"Error queueing message: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/<int:message_id>/mark-read', methods=['POST'])
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # Check if message exists
            cursor = conn.execute("SELECT id, status FROM messages WHERE id = ?", (message_id,))
            message = cursor.fetchone()
            
            if not message:
                return jsonify({'success': False, 'error': 'Message not found'}), 404
            
            # Update status to read
            conn.execute("""
                UPDATE messages 
                SET status = 'read', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (message_id,))
            conn.commit()
            
            logger.info(f"Message {message_id} marked as read")
            return jsonify({'success': True, 'message': f'Message {message_id} marked as read'})
            
    except Exception as e:
        logger.error(f"Error marking message as read: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'unread'")
            unread = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'queued'")
            queued = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'sent'")
            sent = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'failed'")
            failed = cursor.fetchone()[0]
            
            return jsonify({
                'success': True,
                'status': {
                    'total_messages': total,
                    'unread_messages': unread,
                    'queued_messages': queued,
                    'sent_messages': sent,
                    'failed_messages': failed,
                    'timestamp': datetime.now().isoformat()
                }
            })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/messages/recent', methods=['GET'])
def get_recent_messages():
    """Get recent messages (last 20)"""
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT id, phone_number, content, timestamp, status, direction, retry_count
                FROM messages
                ORDER BY id DESC
                LIMIT ?
            """, (limit,))
            messages = [dict(row) for row in cursor.fetchall()]
            
            return jsonify({
                'success': True,
                'count': len(messages),
                'messages': messages,
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error getting recent messages: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messages")
            total_messages = cursor.fetchone()[0]
        
        return jsonify({
            'success': True, 
            'status': 'healthy',
            'database_connected': True,
            'total_messages': total_messages,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """Get specific message by ID"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM messages WHERE id = ?
            """, (message_id,))
            message = cursor.fetchone()
            
            if not message:
                return jsonify({'success': False, 'error': 'Message not found'}), 404
            
            return jsonify({
                'success': True,
                'message': dict(message)
            })
    except Exception as e:
        logger.error(f"Error getting message {message_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({'success': False, 'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("SMSConductor REST API Server")
    print("=" * 50)
    print(f"Database: {DB_PATH}")
    print(f"Port: 5001")
    print("Endpoints:")
    print("  GET  /api/messages/unread     - Get unread messages")
    print("  POST /api/messages/mark-read   - Mark message as read")
    print("  POST /api/messages/send        - Queue message for sending")
    print("  GET  /api/status               - Get system status")
    print("  GET  /api/health               - Health check")
    print("  GET  /api/messages/recent      - Get recent messages")
    print("  GET  /api/messages/<id>        - Get specific message")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
