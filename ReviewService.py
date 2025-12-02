from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/review_service'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255))

class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='reviews')

class Moderation(db.Model):
    __tablename__ = 'moderation'
    review_id = db.Column(db.Integer, db.ForeignKey('reviews.review_id'), primary_key=True)
    moderated_by = db.Column(db.Integer)
    moderated_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False)

@app.route('/reviews', methods=['POST'])
def add_review():
    data = request.json
    new_review = Review(
        service_id=data['service_id'],
        user_id=data['user_id'],
        rating=data['rating'],
        comment=data.get('comment', '')
    )
    db.session.add(new_review)
    db.session.commit()
    return jsonify({'message': 'Review added successfully'}), 201

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def moderate_review(review_id):
    data = request.json
    review = Review.query.get_or_404(review_id)
    review.status = data['status']
    new_moderation = Moderation(
        review_id=review_id,
        moderated_by=data['moderated_by'],
        status=data['status']
    )
    db.session.add(new_moderation)
    db.session.commit()
    return jsonify({'message': 'Review moderated successfully'}), 200

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    return jsonify({'message': 'Review deleted successfully'}), 200

@app.route('/reviews/service/<int:service_id>', methods=['GET'])
def get_reviews(service_id):
    reviews = Review.query.filter_by(service_id=service_id, status='approved').all()
    result = [{
        'review_id': review.review_id,
        'user_id': review.user_id,
        'first_name': review.user.first_name,
        'last_name': review.user.last_name,
        'rating': review.rating,
        'comment': review.comment,
        'created_at': review.created_at
    } for review in reviews]
    return jsonify(result), 200

@app.route('/reviews/service/<int:service_id>/rating', methods=['GET'])
def get_service_rating(service_id):
    reviews = Review.query.filter_by(service_id=service_id, status='approved').all()
    if not reviews:
        return jsonify({'rating': None}), 200
    average_rating = sum([review.rating for review in reviews]) / len(reviews)
    return jsonify({'average_rating': average_rating}), 200

if __name__ == '__main__':
    app.run(debug=True)
