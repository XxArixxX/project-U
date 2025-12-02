from flask import Flask, request, jsonify

app = Flask(__name__)

services = {}

# Создание новой услуги
@app.route('/service/details', methods=['POST'])
def create_service():
    data = request.json
    service_id = data.get('service_id')
    details = data.get('details')
    services[service_id] = details
    return jsonify({'message': 'Service created successfully'}), 201

# Получение детальной информации об услуге по идентификатору
@app.route('/service/details/<service_id>', methods=['GET'])
def get_service(service_id):
    if service_id in services:
        return jsonify(services[service_id]), 200
    else:
        return jsonify({'error': 'Service not found'}), 404

# Обновление детальной информации об услуге
@app.route('/service/details/<service_id>', methods=['PUT'])
def update_service(service_id):
    if service_id in services:
        data = request.json
        services[service_id] = data.get('details')
        return jsonify({'message': 'Service updated successfully'}), 200
    else:
        return jsonify({'error': 'Service not found'}), 404

# Удаление услуги по идентификатору
@app.route('/service/details/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    if service_id in services:
        del services[service_id]
        return jsonify({'message': 'Service deleted successfully'}), 200
    else:
        return jsonify({'error': 'Service not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
