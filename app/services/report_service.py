from datetime import date, timedelta
from sqlalchemy import func
from app.models import db, Product, StockMovement


class ReportService:

    @staticmethod
    def inventory_turnover(days=30):
        cutoff = date.today() - timedelta(days=days)
        results = db.session.query(
            Product.id,
            Product.sku,
            Product.name,
            func.coalesce(func.sum(StockMovement.quantity), 0).label('total_out')
        ).outerjoin(
            StockMovement,
            (StockMovement.product_id == Product.id) &
            (StockMovement.type == 'out') &
            (StockMovement.date >= cutoff)
        ).group_by(Product.id).all()

        turnover = []
        for row in results:
            avg_stock = row.total_out / 2 if row.total_out else 0
            turnover.append({
                'product_id': row.id,
                'sku': row.sku,
                'name': row.name,
                'total_out': float(row.total_out),
                'turnover_rate': round(float(row.total_out / avg_stock), 2) if avg_stock else 0,
            })
        return sorted(turnover, key=lambda x: x['turnover_rate'], reverse=True)

    @staticmethod
    def top_moving_products(limit=10, days=30):
        cutoff = date.today() - timedelta(days=days)
        results = db.session.query(
            Product.id,
            Product.sku,
            Product.name,
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
                'total_moved': float(r.total_moved),
            }
            for r in results
        ]
