from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/chat_service'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Chat(db.Model):
    __tablename__ = 'chats'
    chat_id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    seller_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    message_id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.chat_id'), nullable=False)
    sender_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/chats', methods=['POST'])
def create_chat():
    data = request.json
    new_chat = Chat(
        client_id=data['client_id'],
        seller_id=data['seller_id']
    )
    db.session.add(new_chat)
    db.session.commit()
    return jsonify({'message': 'Chat created successfully', 'chat_id': new_chat.chat_id}), 201

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.json
    new_message = Message(
        chat_id=data['chat_id'],
        sender_id=data['sender_id'],
        message=data['message']
    )
    db.session.add(new_message)
    db.session.commit()

    # Add notification for recipient
    recipient_id = data['recipient_id']
    notification = Notification(
        user_id=recipient_id,
        message=f"New message from user {data['sender_id']} in chat {data['chat_id']}"
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}), 201

@app.route('/messages/<int:chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.sent_at).all()
    result = [{
        'message_id': msg.message_id,
        'chat_id': msg.chat_id,
        'sender_id': msg.sender_id,
        'message': msg.message,
        'sent_at': msg.sent_at
    } for msg in messages]
    return jsonify(result), 200

@app.route('/notifications/<int:user_id>', methods=['GET'])
def get_notifications(user_id):
    notifications = Notification.query.filter_by(user_id=user_id, is_read=False).order_by(Notification.created_at).all()
    result = [{
        'notification_id': notif.notification_id,
        'message': notif.message,
        'created_at': notif.created_at,
        'is_read': notif.is_read
    } for notif in notifications]
    return jsonify(result), 200

@app.route('/notifications/<int:notification_id>', methods=['PUT'])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    return jsonify({'message': 'Notification marked as read'}), 200

if __name__ == '__main__':
    app.run(debug=True)
