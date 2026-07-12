from datetime import date
import requests as http_requests
from flask import current_app
from app.models import db, ExchangeRate


class ExchangeRateService:

    API_BASE = 'https://v6.exchangerate-api.com/v6'

    @classmethod
    def fetch_from_api(cls):
        api_key = current_app.config.get('EXCHANGE_RATE_API_KEY', '')
        if not api_key or api_key == 'your-api-key-here':
            return False, 'API key not configured'

        url = f'{cls.API_BASE}/{api_key}/latest/GEL'
        try:
            resp = http_requests.get(url, timeout=10)
            data = resp.json()
        except Exception as e:
            return False, f'API request failed: {e}'

        if data.get('result') != 'success':
            return False, data.get('error-type', 'unknown error')

        today = date.today()
        rates = data.get('conversion_rates', {})

        for currency, api_rate in rates.items():
            if currency == 'GEL' or api_rate == 0:
                continue
            stored_rate = round(1 / api_rate, 6)
            existing = ExchangeRate.query.filter_by(
                target_currency=currency,
                date=today,
            ).first()
            if existing:
                existing.rate = stored_rate
                existing.source = 'api'
            else:
                db.session.add(ExchangeRate(
                    base_currency='GEL',
                    target_currency=currency,
                    rate=stored_rate,
                    date=today,
                    source='api',
                ))

        db.session.commit()
        return True, 'Rates updated from API'

    @staticmethod
    def get_rate(target_currency):
        if target_currency == 'GEL':
            return 1.0
        rate = ExchangeRate.query.filter_by(
            target_currency=target_currency,
        ).order_by(ExchangeRate.date.desc()).first()
        if rate:
            return rate.rate
        return None

    @staticmethod
    def convert(amount, from_currency, to_currency='GEL'):
        if from_currency == to_currency:
            return amount
        from_rate = ExchangeRateService.get_rate(from_currency)
        to_rate = ExchangeRateService.get_rate(to_currency)
        if from_rate is None or to_rate is None:
            return None
        return round(amount * from_rate / to_rate, 4)

    @staticmethod
    def get_available_currencies():
        codes = db.session.query(ExchangeRate.target_currency).distinct().all()
        result = sorted([r.target_currency for r in codes])
        if 'GEL' not in result:
            result.insert(0, 'GEL')
        return result

    @staticmethod
    def get_all_rates():
        rates = ExchangeRate.query.order_by(ExchangeRate.date.desc()).all()
        return [r.to_dict() for r in rates]

    @staticmethod
    def get_last_updated():
        latest = ExchangeRate.query.order_by(ExchangeRate.date.desc()).first()
        if latest:
            return latest.date
        return None
