from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/monitoring_service'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Log(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, primary_key=True)
    service_name = db.Column(db.String(255), nullable=False)
    log_level = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/logs', methods=['POST'])
def create_log():
    data = request.json
    new_log = Log(
        service_name=data['service_name'],
        log_level=data['log_level'],
        message=data['message']
    )
    db.session.add(new_log)
    db.session.commit()
    return jsonify({'message': 'Log created successfully', 'log_id': new_log.log_id}), 201

@app.route('/logs', methods=['GET'])
def get_logs():
    logs = Log.query.all()
    log_list = []
    for log in logs:
        log_data = {
            'log_id': log.log_id,
            'service_name': log.service_name,
            'log_level': log.log_level,
            'message': log.message,
            'timestamp': log.timestamp
        }
        log_list.append(log_data)
    return jsonify(log_list), 200

@app.route('/logs/<int:log_id>', methods=['GET'])
def get_log(log_id):
    log = Log.query.get_or_404(log_id)
    log_data = {
        'log_id': log.log_id,
        'service_name': log.service_name,
        'log_level': log.log_level,
        'message': log.message,
        'timestamp': log.timestamp
    }
    return jsonify(log_data), 200

@app.route('/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    log = Log.query.get_or_404(log_id)
    db.session.delete(log)
    db.session.commit()
    return jsonify({'message': 'Log deleted successfully'}), 200

@app.route('/logs/search', methods=['GET'])
def search_logs():
    service_name = request.args.get('service_name')
    log_level = request.args.get('log_level')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    query = Log.query
    if service_name:
        query = query.filter_by(service_name=service_name)
    if log_level:
        query = query.filter_by(log_level=log_level)
    if start_time:
        query = query.filter(Log.timestamp >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
    if end_time:
        query = query.filter(Log.timestamp <= datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
    
    logs = query.all()
    log_list = []
    for log in logs:
        log_data = {
            'log_id': log.log_id,
            'service_name': log.service_name,
            'log_level': log.log_level,
            'message': log.message,
            'timestamp': log.timestamp
        }
        log_list.append(log_data)
    return jsonify(log_list), 200

if __name__ == '__main__':
    app.run(debug=True)
