import csv
import io
from app.models import db, Product


class ProductService:

    @staticmethod
    def get_all(category=None, search=None):
        query = Product.query
        if category:
            query = query.filter_by(category=category)
        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        return query.order_by(Product.name).all()

    @staticmethod
    def get_by_id(product_id):
        return Product.query.get_or_404(product_id)

    @staticmethod
    def create(data):
        product = Product(
            sku=data['sku'],
            name=data['name'],
            category=data.get('category'),
            unit=data.get('unit', 'pcs'),
            current_stock=data.get('current_stock', 0),
            min_stock=data.get('min_stock', 0),
            purchase_price=data.get('purchase_price', 0),
            sell_price=data.get('sell_price', 0),
            currency=data.get('currency', 'GEL'),
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update(product_id, data):
        product = Product.query.get_or_404(product_id)
        for field in ['sku', 'name', 'category', 'unit', 'current_stock',
                       'min_stock', 'purchase_price', 'sell_price', 'currency']:
            if field in data:
                setattr(product, field, data[field])
        db.session.commit()
        return product

    @staticmethod
    def delete(product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()

    @staticmethod
    def import_csv(file_content):
        reader = csv.DictReader(io.StringIO(file_content))
        products = []
        for row in reader:
            product = Product(
                sku=row['sku'],
                name=row['name'],
                category=row.get('category'),
                unit=row.get('unit', 'pcs'),
                current_stock=float(row.get('current_stock', 0)),
                min_stock=float(row.get('min_stock', 0)),
                purchase_price=float(row.get('purchase_price', 0)),
                sell_price=float(row.get('sell_price', 0)),
                currency=row.get('currency', 'GEL'),
            )
            db.session.add(product)
            products.append(product)
        db.session.commit()
        return products

    @staticmethod
    def get_low_stock():
        return Product.query.filter(Product.current_stock < Product.min_stock).all()

    @staticmethod
    def get_inventory_value():
        products = Product.query.all()
        total = sum(p.current_stock * p.purchase_price for p in products)
        return {'total_gel': round(total, 2), 'product_count': len(products)}
