from datetime import date
from flask import render_template, redirect, url_for, request, flash, session, abort, current_app
from app.main import bp
from app.main.forms import (ProductForm, SupplierForm, StockInForm,
                            StockOutForm)
from app.models import db, Product, Supplier, StockMovement, ExchangeRate, User
from app.services.product_service import ProductService
from app.services.supplier_service import SupplierService
from app.services.stock_service import StockService
from app.services.report_service import ReportService
from app.services.exchange_rate_service import ExchangeRateService
from app.auth.decorators import login_required


@bp.route('/')
def index():
    return redirect(url_for('main.dashboard'))


@bp.route('/dashboard')
def dashboard():
    low_stock = Product.query.filter(Product.current_stock < Product.min_stock).all()
    products = Product.query.all()
    inventory_value = sum(p.current_stock * p.purchase_price for p in products)
    return render_template('main/dashboard.html',
                           low_stock=low_stock,
                           inventory_value=round(inventory_value, 2),
                           product_count=len(products))


@bp.route('/products')
def product_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    result = ProductService.get_all(page=page, per_page=per_page,
                                    category=category or None,
                                    search=search or None)
    categories = db.session.query(Product.category).distinct().filter(Product.category.isnot(None)).all()
    categories = [c[0] for c in categories]
    return render_template('main/products.html', data=result,
                           search=search, category=category,
                           categories=categories)


@bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def product_create():
    form = ProductForm()
    if form.validate_on_submit():
        ProductService.create({
            'sku': form.sku.data,
            'name': form.name.data,
            'category': form.category.data,
            'unit': form.unit.data,
            'current_stock': form.current_stock.data,
            'min_stock': form.min_stock.data,
            'purchase_price': form.purchase_price.data,
            'sell_price': form.sell_price.data,
            'currency': form.currency.data,
            'created_by': session['user_id'],
        })
        flash('Product created.', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('main/product_form.html', form=form, title='New Product')


@bp.route('/products/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    page = request.args.get('page', 1, type=int)
    movements = StockService.get_movements(product_id, page=page, per_page=15)
    return render_template('main/product_detail.html', product=product, movements=movements)


@bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    product = Product.query.get_or_404(product_id)
    user = User.query.get(session['user_id'])
    if product.created_by and product.created_by != session['user_id'] and not user.is_admin:
        abort(403)
    form = ProductForm(obj=product, original_sku=product.sku)
    if form.validate_on_submit():
        ProductService.update(product_id, {
            'sku': form.sku.data,
            'name': form.name.data,
            'category': form.category.data,
            'unit': form.unit.data,
            'current_stock': form.current_stock.data,
            'min_stock': form.min_stock.data,
            'purchase_price': form.purchase_price.data,
            'sell_price': form.sell_price.data,
            'currency': form.currency.data,
        })
        flash('Product updated.', 'success')
        return redirect(url_for('main.product_detail', product_id=product_id))
    return render_template('main/product_form.html', form=form, title='Edit Product')


@bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def product_delete(product_id):
    product = Product.query.get_or_404(product_id)
    user = User.query.get(session['user_id'])
    if product.created_by and product.created_by != session['user_id'] and not user.is_admin:
        abort(403)
    ProductService.delete(product_id)
    flash('Product deleted.', 'success')
    return redirect(url_for('main.product_list'))


@bp.route('/suppliers')
def supplier_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    country = request.args.get('country', '')
    result = SupplierService.get_all(page=page, per_page=per_page,
                                     country=country or None,
                                     search=search or None)
    countries = db.session.query(Supplier.country).distinct().filter(Supplier.country.isnot(None)).all()
    countries = [c[0] for c in countries]
    return render_template('main/suppliers.html', data=result,
                           search=search, country=country,
                           countries=countries)


@bp.route('/suppliers/new', methods=['GET', 'POST'])
@login_required
def supplier_create():
    form = SupplierForm()
    if form.validate_on_submit():
        SupplierService.create({
            'company': form.company.data,
            'contact': form.contact.data,
            'country': form.country.data,
            'lead_time': form.lead_time.data,
            'created_by': session['user_id'],
        })
        flash('Supplier created.', 'success')
        return redirect(url_for('main.supplier_list'))
    return render_template('main/supplier_form.html', form=form, title='New Supplier')


@bp.route('/suppliers/<int:supplier_id>/edit', methods=['GET', 'POST'])
@login_required
def supplier_edit(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    user = User.query.get(session['user_id'])
    if supplier.created_by and supplier.created_by != session['user_id'] and not user.is_admin:
        abort(403)
    form = SupplierForm(obj=supplier)
    if form.validate_on_submit():
        SupplierService.update(supplier_id, {
            'company': form.company.data,
            'contact': form.contact.data,
            'country': form.country.data,
            'lead_time': form.lead_time.data,
        })
        flash('Supplier updated.', 'success')
        return redirect(url_for('main.supplier_list'))
    return render_template('main/supplier_form.html', form=form, title='Edit Supplier')


@bp.route('/suppliers/<int:supplier_id>/delete', methods=['POST'])
@login_required
def supplier_delete(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    user = User.query.get(session['user_id'])
    if supplier.created_by and supplier.created_by != session['user_id'] and not user.is_admin:
        abort(403)
    SupplierService.delete(supplier_id)
    flash('Supplier deleted.', 'success')
    return redirect(url_for('main.supplier_list'))


@bp.route('/stock-in', methods=['GET', 'POST'])
@login_required
def stock_in():
    form = StockInForm()
    form.product_id.choices = [(p.id, f'{p.sku} - {p.name}') for p in Product.query.order_by(Product.name).all()]
    form.supplier_id.choices = [(0, '-- None --')] + [(s.id, s.company) for s in Supplier.query.order_by(Supplier.company).all()]
    if form.validate_on_submit():
        supplier_id = form.supplier_id.data if form.supplier_id.data else None
        StockService.stock_in(
            product_id=form.product_id.data,
            quantity=form.quantity.data,
            cost_per_unit=form.cost_per_unit.data or None,
            supplier_id=supplier_id,
            reference=form.reference.data,
        )
        flash('Stock received.', 'success')
        return redirect(url_for('main.dashboard'))
    return render_template('main/stock_form.html', form=form, title='Stock IN')


@bp.route('/stock-out', methods=['GET', 'POST'])
@login_required
def stock_out():
    form = StockOutForm()
    form.product_id.choices = [(p.id, f'{p.sku} - {p.name}') for p in Product.query.order_by(Product.name).all()]
    if form.validate_on_submit():
        try:
            StockService.stock_out(
                product_id=form.product_id.data,
                quantity=form.quantity.data,
                destination=form.destination.data,
                reference=form.reference.data,
            )
            flash('Stock issued.', 'success')
            return redirect(url_for('main.dashboard'))
        except ValueError as e:
            flash(str(e), 'danger')
    return render_template('main/stock_form.html', form=form, title='Stock OUT')


@bp.route('/alerts')
def alerts():
    page = request.args.get('page', 1, type=int)
    result = ProductService.get_low_stock(page=page, per_page=20)
    return render_template('main/alerts.html', data=result)


@bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('main.import_csv'))
        file = request.files['file']
        if not file.filename.endswith('.csv'):
            flash('File must be a CSV.', 'danger')
            return redirect(url_for('main.import_csv'))
        content = file.read().decode('utf-8')
        products = ProductService.import_csv(content, created_by=session['user_id'])
        flash(f'Imported {len(products)} products.', 'success')
        return redirect(url_for('main.product_list'))
    return render_template('main/import_csv.html')


@bp.route('/exchange-rates', methods=['GET', 'POST'])
def exchange_rates():
    if request.method == 'POST':
        success, message = ExchangeRateService.fetch_from_api()
        flash(message, 'success' if success else 'danger')
        return redirect(url_for('main.exchange_rates'))

    rates = ExchangeRateService.get_all_rates()
    last_updated = ExchangeRateService.get_last_updated()
    currencies = ExchangeRateService.get_available_currencies()
    api_key_set = bool(
        current_app.config.get('EXCHANGE_RATE_API_KEY')
        and current_app.config.get('EXCHANGE_RATE_API_KEY') != 'your-api-key-here'
    )
    return render_template('main/exchange_rates.html',
                           rates=rates,
                           currencies=currencies,
                           last_updated=last_updated,
                           api_key_set=api_key_set)


@bp.route('/reports')
def reports():
    days = request.args.get('days', 30, type=int)
    turnover = ReportService.inventory_turnover(days=days, page=1, per_page=50)
    top_products = ReportService.top_moving_products(limit=10, days=days)
    return render_template('main/reports.html', turnover=turnover,
                           top_products=top_products, days=days)
