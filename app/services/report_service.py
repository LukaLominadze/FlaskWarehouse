from datetime import date, timedelta
from sqlalchemy import func
from app.models import db, Product, StockMovement
from app.utils import paginate_query


class ReportService:

    @staticmethod
    def inventory_turnover(days=30, page=1, per_page=20):
        cutoff = date.today() - timedelta(days=days)
        base_query = db.session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.current_stock,
            func.coalesce(func.sum(StockMovement.quantity), 0).label('total_out')
        ).outerjoin(
            StockMovement,
            (StockMovement.product_id == Product.id) &
            (StockMovement.type == 'out') &
            (StockMovement.date >= cutoff)
        ).group_by(Product.id)

        per_page = max(10, min(per_page, 100))
        total = base_query.count()
        items = base_query.order_by(Product.name)\
            .offset((page - 1) * per_page)\
            .limit(per_page).all()

        turnover = []
        for row in items:
            avg_stock = row.total_out / 2 if row.total_out else 0
            turnover.append({
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'current_stock': row.current_stock,
                'total_out': float(row.total_out),
                'turnover_rate': round(float(row.total_out / avg_stock), 2) if avg_stock else 0,
            })

        return {
            'items': turnover,
            'total': total,
            'pages': (total + per_page - 1) // per_page,
            'current_page': page,
            'per_page': per_page,
        }

    @staticmethod
    def top_moving_products(limit=10, days=30):
        cutoff = date.today() - timedelta(days=days)
        limit = max(1, min(limit, 100))
        results = db.session.query(
            Product.id,
            Product.sku,
            Product.name,
            Product.current_stock,
            func.sum(StockMovement.quantity).label('total_moved')
        ).join(
            StockMovement, StockMovement.product_id == Product.id
        ).filter(
            StockMovement.type == 'out',
            StockMovement.date >= cutoff
        ).group_by(Product.id)\
         .order_by(func.sum(StockMovement.quantity).desc())\
         .limit(limit).all()

        return [
            {
                'product_id': r.id,
                'sku': r.sku,
                'name': r.name,
                'current_stock': r.current_stock,
                'total_moved': float(r.total_moved),
            }
            for r in results
        ]
