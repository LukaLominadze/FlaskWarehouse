from flask import request, jsonify
from app.api import bp
from app.services.product_service import ProductService
from app.services.supplier_service import SupplierService
from app.services.stock_service import StockService
from app.services.report_service import ReportService
from app.services.exchange_rate_service import ExchangeRateService


@bp.route('/status')
def status():
    return {'status': 'ok'}


@bp.route('/products', methods=['GET'])
def get_products():
    category = request.args.get('category')
    search = request.args.get('search')
    products = ProductService.get_all(category=category, search=search)
    return jsonify([p.to_dict() for p in products])


@bp.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    if not data or 'sku' not in data or 'name' not in data:
        return jsonify({'error': 'sku and name are required'}), 400
    product = ProductService.create(data)
    return jsonify(product.to_dict()), 201


@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductService.get_by_id(product_id)
    return jsonify(product.to_dict())


@bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = ProductService.update(product_id, data)
    return jsonify(product.to_dict())


@bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    ProductService.delete(product_id)
    return '', 204


@bp.route('/products/import', methods=['POST'])
def import_products():
    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400
    file = request.files['file']
    content = file.read().decode('utf-8')
    products = ProductService.import_csv(content)
    return jsonify({'imported': len(products)}), 201


@bp.route('/products/<int:product_id>/movements', methods=['GET'])
def get_movements(product_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    result = StockService.get_movements(product_id, page=page, per_page=per_page)
    return jsonify(result)


@bp.route('/stock-in', methods=['POST'])
def stock_in():
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'product_id and quantity are required'}), 400
    try:
        movement = StockService.stock_in(
            product_id=data['product_id'],
            quantity=data['quantity'],
            cost_per_unit=data.get('cost_per_unit'),
            supplier_id=data.get('supplier_id'),
            reference=data.get('reference'),
        )
        return jsonify(movement.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/stock-out', methods=['POST'])
def stock_out():
    data = request.get_json()
    if not data or 'product_id' not in data or 'quantity' not in data:
        return jsonify({'error': 'product_id and quantity are required'}), 400
    try:
        movement = StockService.stock_out(
            product_id=data['product_id'],
            quantity=data['quantity'],
            destination=data.get('destination'),
            reference=data.get('reference'),
        )
        return jsonify(movement.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/alerts', methods=['GET'])
def get_alerts():
    products = ProductService.get_low_stock()
    return jsonify([p.to_dict() for p in products])


@bp.route('/inventory-value', methods=['GET'])
def get_inventory_value():
    result = ProductService.get_inventory_value()
    return jsonify(result)


@bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    country = request.args.get('country')
    suppliers = SupplierService.get_all(country=country)
    return jsonify([s.to_dict() for s in suppliers])


@bp.route('/suppliers', methods=['POST'])
def create_supplier():
    data = request.get_json()
    if not data or 'company' not in data:
        return jsonify({'error': 'company is required'}), 400
    supplier = SupplierService.create(data)
    return jsonify(supplier.to_dict()), 201


@bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    data = request.get_json()
    supplier = SupplierService.update(supplier_id, data)
    return jsonify(supplier.to_dict())


@bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    SupplierService.delete(supplier_id)
    return '', 204


@bp.route('/exchange-rates', methods=['GET'])
def get_exchange_rates():
    return jsonify(ExchangeRateService.get_all_rates())


@bp.route('/exchange-rates', methods=['POST'])
def update_exchange_rate():
    data = request.get_json()
    if not data or 'currency' not in data or 'rate' not in data:
        return jsonify({'error': 'currency and rate are required'}), 400
    ExchangeRateService.update_rate(data['currency'], data['rate'])
    return jsonify({'status': 'updated'})


@bp.route('/convert', methods=['GET'])
def convert_currency():
    amount = request.args.get('amount', 0, type=float)
    from_currency = request.args.get('from', 'USD')
    result = ExchangeRateService.convert(amount, from_currency)
    return jsonify({'amount': amount, 'from': from_currency, 'to': 'GEL', 'result': result})


@bp.route('/reports/turnover', methods=['GET'])
def get_turnover():
    days = request.args.get('days', 30, type=int)
    return jsonify(ReportService.inventory_turnover(days=days))


@bp.route('/reports/top-products', methods=['GET'])
def get_top_products():
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 10, type=int)
    return jsonify(ReportService.top_moving_products(limit=limit, days=days))
