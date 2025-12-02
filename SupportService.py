from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/support_service'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class SupportTicket(db.Model):
    __tablename__ = 'support_tickets'
    ticket_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class KnowledgeBase(db.Model):
    __tablename__ = 'knowledge_base'
    article_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.json
    new_ticket = SupportTicket(
        user_id=data['user_id'],
        subject=data['subject'],
        description=data['description']
    )
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket created successfully', 'ticket_id': new_ticket.ticket_id}), 201

@app.route('/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    return jsonify({
        'ticket_id': ticket.ticket_id,
        'user_id': ticket.user_id,
        'subject': ticket.subject,
        'description': ticket.description,
        'status': ticket.status,
        'created_at': ticket.created_at,
        'updated_at': ticket.updated_at
    }), 200

@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    data = request.json
    ticket = SupportTicket.query.get_or_404(ticket_id)
    ticket.subject = data.get('subject', ticket.subject)
    ticket.description = data.get('description', ticket.description)
    ticket.status = data.get('status', ticket.status)
    db.session.commit()
    return jsonify({'message': 'Ticket updated successfully'}), 200

@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted successfully'}), 200

@app.route('/knowledge_base', methods=['POST'])
def create_article():
    data = request.json
    new_article = KnowledgeBase(
        title=data['title'],
        content=data['content']
    )
    db.session.add(new_article)
    db.session.commit()
    return jsonify({'message': 'Article created successfully', 'article_id': new_article.article_id}), 201

@app.route('/knowledge_base/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = KnowledgeBase.query.get_or_404(article_id)
    return jsonify({
        'article_id': article.article_id,
        'title': article.title,
        'content': article.content,
        'created_at': article.created_at,
        'updated_at': article.updated_at
    }), 200

@app.route('/knowledge_base/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    data = request.json
    article = KnowledgeBase.query.get_or_404(article_id)
    article.title = data.get('title', article.title)
    article.content = data.get('content', article.content)
    db.session.commit()
    return jsonify({'message': 'Article updated successfully'}), 200

@app.route('/knowledge_base/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    article = KnowledgeBase.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': 'Article deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
