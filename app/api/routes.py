from flask import request, jsonify, session
from app.api import bp
from app.auth.decorators import login_required
from app.services.product_service import ProductService
from app.services.supplier_service import SupplierService
from app.services.stock_service import StockService
from app.services.report_service import ReportService
from app.services.exchange_rate_service import ExchangeRateService
from app.models import Product, Supplier, User


@bp.route('/status')
def status():
    return {'status': 'ok'}


@bp.route('/products', methods=['GET'])
def get_products():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    search = request.args.get('search')
    sort_by = request.args.get('sort_by', 'name')
    sort_dir = request.args.get('sort_dir', 'asc')
    return jsonify(ProductService.get_all(
        page=page, per_page=per_page, category=category,
        search=search, sort_by=sort_by, sort_dir=sort_dir
    ))


@bp.route('/products', methods=['POST'])
@login_required
def create_product():
    data = request.get_json()
    if not data or 'sku' not in data or 'name' not in data:
        return jsonify({'error': 'sku and name are required'}), 400
    data['created_by'] = session['user_id']
    product = ProductService.create(data)
    return jsonify(product.to_dict()), 201


@bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = ProductService.get_by_id(product_id)
    return jsonify(product.to_dict())


@bp.route('/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    user = User.query.get(session['user_id'])
    if product.created_by and product.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json()
    product = ProductService.update(product_id, data)
    return jsonify(product.to_dict())


@bp.route('/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    user = User.query.get(session['user_id'])
    if product.created_by and product.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'forbidden'}), 403
    ProductService.delete(product_id)
    return '', 204


@bp.route('/products/import', methods=['POST'])
@login_required
def import_products():
    if 'file' not in request.files:
        return jsonify({'error': 'no file provided'}), 400
    file = request.files['file']
    content = file.read().decode('utf-8')
    products = ProductService.import_csv(content, created_by=session['user_id'])
    return jsonify({'imported': len(products)}), 201


@bp.route('/products/<int:product_id>/movements', methods=['GET'])
def get_movements(product_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    movement_type = request.args.get('type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    result = StockService.get_movements(
        product_id, page=page, per_page=per_page,
        movement_type=movement_type, date_from=date_from, date_to=date_to
    )
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
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(ProductService.get_low_stock(page=page, per_page=per_page))


@bp.route('/inventory-value', methods=['GET'])
def get_inventory_value():
    result = ProductService.get_inventory_value()
    return jsonify(result)


@bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    country = request.args.get('country')
    search = request.args.get('search')
    return jsonify(SupplierService.get_all(
        page=page, per_page=per_page, country=country, search=search
    ))


@bp.route('/suppliers', methods=['POST'])
@login_required
def create_supplier():
    data = request.get_json()
    if not data or 'company' not in data:
        return jsonify({'error': 'company is required'}), 400
    data['created_by'] = session['user_id']
    supplier = SupplierService.create(data)
    return jsonify(supplier.to_dict()), 201


@bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
@login_required
def update_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    user = User.query.get(session['user_id'])
    if supplier.created_by and supplier.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'forbidden'}), 403
    data = request.get_json()
    supplier = SupplierService.update(supplier_id, data)
    return jsonify(supplier.to_dict())


@bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
@login_required
def delete_supplier(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    user = User.query.get(session['user_id'])
    if supplier.created_by and supplier.created_by != session['user_id'] and not user.is_admin:
        return jsonify({'error': 'forbidden'}), 403
    SupplierService.delete(supplier_id)
    return '', 204


@bp.route('/exchange-rates', methods=['GET'])
def get_exchange_rates():
    return jsonify(ExchangeRateService.get_all_rates())


@bp.route('/convert', methods=['GET'])
def convert_currency():
    amount = request.args.get('amount', 1, type=float)
    from_currency = request.args.get('from', 'USD')
    to_currency = request.args.get('to', 'GEL')
    result = ExchangeRateService.convert(amount, from_currency, to_currency)
    if result is None:
        return jsonify({'error': 'rate not available'}), 400
    return jsonify({'amount': amount, 'from': from_currency, 'to': to_currency, 'result': result})


@bp.route('/exchange-rates/refresh', methods=['POST'])
def refresh_exchange_rates():
    success, message = ExchangeRateService.fetch_from_api()
    if not success:
        return jsonify({'error': message}), 400
    rates = ExchangeRateService.get_all_rates()
    return jsonify({'status': 'refreshed', 'rates': rates})


@bp.route('/reports/turnover', methods=['GET'])
def get_turnover():
    days = request.args.get('days', 30, type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    return jsonify(ReportService.inventory_turnover(days=days, page=page, per_page=per_page))


@bp.route('/reports/top-products', methods=['GET'])
def get_top_products():
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 10, type=int)
    return jsonify(ReportService.top_moving_products(limit=limit, days=days))
