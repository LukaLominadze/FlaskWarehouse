from datetime import date
from app.models import db, Product, StockMovement
from app.utils import paginate_query


class StockService:

    @staticmethod
    def stock_in(product_id, quantity, cost_per_unit=None, supplier_id=None,
                 reference=None, movement_date=None):
        product = Product.query.get_or_404(product_id)
        product.current_stock += quantity

        movement = StockMovement(
            product_id=product_id,
            type='in',
            supplier_id=supplier_id,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            date=movement_date or date.today(),
            reference=reference,
        )
        db.session.add(movement)
        db.session.commit()
        return movement

    @staticmethod
    def stock_out(product_id, quantity, destination=None,
                  reference=None, movement_date=None):
        product = Product.query.get_or_404(product_id)
        if product.current_stock < quantity:
            raise ValueError('Insufficient stock')

        product.current_stock -= quantity

        movement = StockMovement(
            product_id=product_id,
            type='out',
            quantity=quantity,
            date=movement_date or date.today(),
            reference=reference,
            destination=destination,
        )
        db.session.add(movement)
        db.session.commit()
        return movement

    @staticmethod
    def get_movements(product_id, page=1, per_page=20, movement_type=None,
                      date_from=None, date_to=None):
        query = StockMovement.query.filter_by(product_id=product_id)
        if movement_type:
            query = query.filter_by(type=movement_type)
        if date_from:
            query = query.filter(StockMovement.date >= date_from)
        if date_to:
            query = query.filter(StockMovement.date <= date_to)
        query = query.order_by(StockMovement.date.desc())
        return paginate_query(query, page, per_page)
