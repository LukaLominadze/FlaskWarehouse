from datetime import date
from app.models import db, ExchangeRate


class ExchangeRateService:

    RATES = {
        'USD': 2.75,
        'EUR': 3.00,
        'TRY': 0.085,
        'GBP': 3.50,
        'RUB': 0.03,
    }

    @staticmethod
    def get_rate(target_currency):
        rate = ExchangeRate.query.filter_by(
            target_currency=target_currency
        ).order_by(ExchangeRate.date.desc()).first()
        if rate:
            return rate.rate
        return ExchangeRateService.RATES.get(target_currency, 1.0)

    @staticmethod
    def convert(amount, from_currency, to_currency='GEL'):
        if from_currency == to_currency:
            return amount
        rate = ExchangeRateService.get_rate(from_currency)
        return round(amount * rate, 2)

    @staticmethod
    def update_rate(target_currency, rate):
        existing = ExchangeRate.query.filter_by(
            target_currency=target_currency,
            date=date.today()
        ).first()
        if existing:
            existing.rate = rate
        else:
            entry = ExchangeRate(
                base_currency='GEL',
                target_currency=target_currency,
                rate=rate,
                date=date.today(),
            )
            db.session.add(entry)
        db.session.commit()

    @staticmethod
    def get_all_rates():
        rates = ExchangeRate.query.order_by(ExchangeRate.date.desc()).all()
        return [r.to_dict() for r in rates]
