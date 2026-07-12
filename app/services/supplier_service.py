from app.models import db, Supplier
from app.utils import paginate_query


class SupplierService:

    @staticmethod
    def get_all(page=1, per_page=20, country=None, search=None):
        query = Supplier.query
        if country:
            query = query.filter_by(country=country)
        if search:
            pattern = f'%{search}%'
            query = query.filter(
                db.or_(
                    Supplier.company.ilike(pattern),
                    Supplier.contact.ilike(pattern),
                )
            )
        query = query.order_by(Supplier.company)
        return paginate_query(query, page, per_page)

    @staticmethod
    def get_by_id(supplier_id):
        return Supplier.query.get_or_404(supplier_id)

    @staticmethod
    def create(data):
        supplier = Supplier(
            company=data['company'],
            contact=data.get('contact'),
            country=data.get('country'),
            lead_time=data.get('lead_time'),
            created_by=data.get('created_by'),
        )
        db.session.add(supplier)
        db.session.commit()
        return supplier

    @staticmethod
    def update(supplier_id, data):
        supplier = Supplier.query.get_or_404(supplier_id)
        for field in ['company', 'contact', 'country', 'lead_time']:
            if field in data:
                setattr(supplier, field, data[field])
        db.session.commit()
        return supplier

    @staticmethod
    def delete(supplier_id):
        supplier = Supplier.query.get_or_404(supplier_id)
        db.session.delete(supplier)
        db.session.commit()
