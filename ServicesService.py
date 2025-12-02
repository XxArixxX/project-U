from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)

# Конфигурация приложения
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Определение моделей
class Client(db.Model):
    __tablename__ = 'clients'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(255))
    picture = db.Column(db.LargeBinary)
    address = db.Column(db.String(255))

class FavoriteSeller(db.Model):
    __tablename__ = 'favorite_sellers'
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

class Ticket(db.Model):
    __tablename__ = 'tickets'
    client_id = db.Column(db.Integer, db.ForeignKey('clients.client_id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.offer_id'), nullable=False)
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Boolean)
    to_pay = db.Column(db.Float)
    feedback = db.Column(db.String(255))
    date_purchase = db.Column(db.Date)

class Seller(db.Model):
    __tablename__ = 'sellers'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    seller_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    passport = db.Column(db.LargeBinary)
    seller_name = db.Column(db.String(255))
    main_picture = db.Column(db.LargeBinary)
    description = db.Column(db.String(255))
    pictures = db.Column(db.ARRAY(db.LargeBinary))
    rating = db.Column(db.Integer)
    category = db.Column(db.String(255))
    price = db.Column(db.Numeric)

class Offer(db.Model):
    __tablename__ = 'offers'
    seller_id = db.Column(db.Integer, db.ForeignKey('sellers.seller_id'), nullable=False)
    offer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    percent = db.Column(db.Float)
    date_offer = db.Column(db.Date)

# Реализация маршрутов

# Пример маршрута для создания нового клиента
@app.route('/clients', methods=['POST'])
def create_client():
    data = request.json
    new_client = Client(
        user_id=data['user_id'],
        user_name=data['user_name'],
        picture=data['picture'],
        address=data['address']
    )
    db.session.add(new_client)
    db.session.commit()
    return jsonify({'message': 'Client created successfully'}), 201

# Пример маршрута для получения списка всех клиентов
@app.route('/clients', methods=['GET'])
def get_clients():
    clients = Client.query.all()
    return jsonify([client.user_name for client in clients]), 200


# Удаление клиента по идентификатору
@app.route('/clients/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    db.session.delete(client)
    db.session.commit()
    return jsonify({'message': 'Client deleted successfully'}), 200

# Изменение данных о клиенте
@app.route('/clients/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    client = Client.query.get(client_id)
    if not client:
        return jsonify({'error': 'Client not found'}), 404
    data = request.json
    client.user_name = data['user_name']
    client.picture = data['picture']
    client.address = data['address']
    db.session.commit()
    return jsonify({'message': 'Client updated successfully'}), 200

# Добавление нового избранного продавца
@app.route('/favorite_sellers', methods=['POST'])
def create_favorite_seller():
    data = request.json
    new_favorite_seller = FavoriteSeller(
        client_id=data['client_id'],
        seller_id=data['seller_id']
    )
    db.session.add(new_favorite_seller)
    db.session.commit()
    return jsonify({'message': 'Favorite seller added successfully'}), 201

# Удаление избранного продавца по идентификатору
@app.route('/favorite_sellers/<int:favorite_id>', methods=['DELETE'])
def delete_favorite_seller(favorite_id):
    favorite_seller = FavoriteSeller.query.get(favorite_id)
    if not favorite_seller:
        return jsonify({'error': 'Favorite seller not found'}), 404
    db.session.delete(favorite_seller)
    db.session.commit()
    return jsonify({'message': 'Favorite seller deleted successfully'}), 200

# Добавление нового тикета
@app.route('/tickets', methods=['POST'])
def create_ticket():
    data = request.json
    new_ticket = Ticket(
        client_id=data['client_id'],
        seller_id=data['seller_id'],
        offer_id=data['offer_id'],
        status=data['status'],
        to_pay=data['to_pay'],
        feedback=data['feedback'],
        date_purchase=data['date_purchase']
    )
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket created successfully'}), 201

# Удаление тикета по идентификатору
@app.route('/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': 'Ticket deleted successfully'}), 200

# Изменение данных о тикете
@app.route('/tickets/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket:
        return jsonify({'error': 'Ticket not found'}), 404
    data = request.json
    ticket.status = data['status']
    ticket.to_pay = data['to_pay']
    ticket.feedback = data['feedback']
    ticket.date_purchase = data['date_purchase']
    db.session.commit()
    return jsonify({'message': 'Ticket updated successfully'}), 200

# Добавление нового продавца
@app.route('/sellers', methods=['POST'])
def create_seller():
    data = request.json
    new_seller = Seller(
        user_id=data['user_id'],
        passport=data['passport'],
        seller_name=data['seller_name'],
        main_picture=data['main_picture'],
        description=data['description'],
        pictures=data['pictures'],
        rating=data['rating'],
        category=data['category'],
        price=data['price']
    )
    db.session.add(new_seller)
    db.session.commit()
    return jsonify({'message': 'Seller created successfully'}), 201

# Удаление продавца по идентификатору
@app.route('/sellers/<int:seller_id>', methods=['DELETE'])
def delete_seller(seller_id):
    seller = Seller.query.get(seller_id)
    if not seller:
        return jsonify({'error': 'Seller not found'}), 404
    db.session.delete(seller)
    db.session.commit()
    return jsonify({'message': 'Seller deleted successfully'}), 200

# Изменение данных о продавце
@app.route('/sellers/<int:seller_id>', methods=['PUT'])
def update_seller(seller_id):
    seller = Seller.query.get(seller_id)
    if not seller:
        return jsonify({'error': 'Seller not found'}), 404
    data = request.json
    seller.passport = data['passport']
    seller.seller_name = data['seller_name']
    seller.main_picture = data['main_picture']
    seller.description = data['description']
    seller.pictures = data['pictures']
    seller.rating = data['rating']
    seller.category = data['category']
    seller.price = data['price']
    db.session.commit()
    return jsonify({'message': 'Seller updated successfully'}), 200

# Добавление нового предложения
@app.route('/offers', methods=['POST'])
def create_offer():
    data = request.json
    new_offer = Offer(
        seller_id=data['seller_id'],
        percent=data['percent'],
        date_offer=data['date_offer']
    )
    db.session.add(new_offer)
    db.session.commit()
    return jsonify({'message': 'Offer created successfully'}), 201

# Удаление предложения по идентификатору
@app.route('/offers/<int:offer_id>', methods=['DELETE'])
def delete_offer(offer_id):
    offer = Offer.query.get(offer_id)
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    db.session.delete(offer)
    db.session.commit()
    return jsonify({'message': 'Offer deleted successfully'}), 200

# Изменение данных о предложении
@app.route('/offers/<int:offer_id>', methods=['PUT'])
def update_offer(offer_id):
    offer = Offer.query.get(offer_id)
    if not offer:
        return jsonify({'error': 'Offer not found'}), 404
    data = request.json
    offer.percent = data['percent']
    offer.date_offer = data['date_offer']
    db.session.commit()
    return jsonify({'message': 'Offer updated successfully'}), 200

# Далее поиск для каждой таблицы
# Поиск клиента по имени
@app.route('/clients/search', methods=['GET'])
def search_clients():
    search_query = request.args.get('q')
    clients = Client.query.filter(Client.user_name.ilike(f'%{search_query}%')).all()
    return jsonify([client.user_name for client in clients]), 200

# Поиск избранных продавцов по идентификатору клиента
@app.route('/favorite_sellers/search', methods=['GET'])
def search_favorite_sellers():
    client_id = request.args.get('client_id')
    favorite_sellers = FavoriteSeller.query.filter_by(client_id=client_id).all()
    return jsonify([fav_seller.seller_id for fav_seller in favorite_sellers]), 200

# Поиск тикетов по идентификатору клиента
@app.route('/tickets/search', methods=['GET'])
def search_tickets():
    client_id = request.args.get('client_id')
    tickets = Ticket.query.filter_by(client_id=client_id).all()
    return jsonify([ticket.ticket_id for ticket in tickets]), 200

# Поиск продавцов по имени
@app.route('/sellers/search', methods=['GET'])
def search_sellers():
    search_query = request.args.get('q')
    sellers = Seller.query.filter(Seller.seller_name.ilike(f'%{search_query}%')).all()
    return jsonify([seller.seller_name for seller in sellers]), 200

# Поиск предложений по идентификатору продавца
@app.route('/offers/search', methods=['GET'])
def search_offers():
    seller_id = request.args.get('seller_id')
    offers = Offer.query.filter_by(seller_id=seller_id).all()
    return jsonify([offer.offer_id for offer in offers]), 200

#Далее поиск по тегам. теги из другого микросервиса берутся
@app.route('/clients/search_by_tag', methods=['GET'])
def search_clients_by_tag():
    tag = request.args.get('tag')
    # Отправляем запрос к микросервису для поиска клиентов по тегу
    response = requests.get(f'http://tag-service/api/clients?tag={tag}')
    if response.status_code == 200:
        clients = response.json()
        # Обработка результатов поиска
        # Например, получение дополнительной информации о клиентах из вашей базы данных
        return jsonify(clients), 200
    else:
        return jsonify({'error': 'Tag service error'}), 500

@app.route('/favorite_sellers/search_by_tag', methods=['GET'])
def search_favorite_sellers_by_tag():
    tag = request.args.get('tag')
    # Отправляем запрос к микросервису для поиска избранных продавцов по тегу
    response = requests.get(f'http://tag-service/api/favorite_sellers?tag={tag}')
    if response.status_code == 200:
        favorite_sellers = response.json()
        # Обработка результатов поиска
        # Например, получение дополнительной информации о продавцах из вашей базы данных
        return jsonify(favorite_sellers), 200
    else:
        return jsonify({'error': 'Tag service error'}), 500

@app.route('/tickets/search_by_tag', methods=['GET'])
def search_tickets_by_tag():
    tag = request.args.get('tag')
    # Отправляем запрос к микросервису для поиска билетов по тегу
    response = requests.get(f'http://tag-service/api/tickets?tag={tag}')
    if response.status_code == 200:
        tickets = response.json()
        # Обработка результатов поиска
        # Например, получение дополнительной информации о билетах из вашей базы данных
        return jsonify(tickets), 200
    else:
        return jsonify({'error': 'Tag service error'}), 500

@app.route('/sellers/search_by_tag', methods=['GET'])
def search_sellers_by_tag():
    tag = request.args.get('tag')
    # Отправляем запрос к микросервису для поиска продавцов по тегу
    response = requests.get(f'http://tag-service/api/sellers?tag={tag}')
    if response.status_code == 200:
        sellers = response.json()
        # Обработка результатов поиска
        # Например, получение дополнительной информации о продавцах из вашей базы данных
        return jsonify(sellers), 200
    else:
        return jsonify({'error': 'Tag service error'}), 500

@app.route('/offers/search_by_tag', methods=['GET'])
def search_offers_by_tag():
    tag = request.args.get('tag')
    # Отправляем запрос к микросервису для поиска предложений по тегу
    response = requests.get(f'http://tag-service/api/offers?tag={tag}')
    if response.status_code == 200:
        offers = response.json()
        # Обработка результатов поиска
        # Например, получение дополнительной информации о предложениях из вашей базы данных
        return jsonify(offers), 200
    else:
        return jsonify({'error': 'Tag service error'}), 500

#Получение детальной информации об услуге. стучится в другой микросервис
@app.route('/service/details', methods=['GET'])
def get_service_details():
    service_id = request.args.get('service_id')
    # Отправляем запрос к микросервису для получения подробной информации об услуге
    response = requests.get(f'http://service-details-service/api/service/details?service_id={service_id}')
    if response.status_code == 200:
        service_details = response.json()
        # Обработка полученных данных
        return jsonify(service_details), 200
    else:
        return jsonify({'error': 'Service details service error'}), 500
if __name__ == '__main__':
    app.run(debug=True)
