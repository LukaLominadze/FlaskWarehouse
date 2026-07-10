from app.models import db, Supplier


class SupplierService:

    @staticmethod
    def get_all(country=None):
        query = Supplier.query
        if country:
            query = query.filter_by(country=country)
        return query.order_by(Supplier.company).all()

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
