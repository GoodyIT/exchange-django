import unittest
from mock import patch


class TestConversion(unittest.TestCase):

    def test_convert(self):
        """Test :py:func:``exchange.conversion.convert``"""
        from exchange.conversion import convert, Price
        with patch('exchange.conversion.ExchangeRates') as exchange_rates:
            exchange_rates.get_instance.return_value = \
                {'USD': {'GBP': 0.5}}
            price = Price(3, 'USD')
            converted_price = convert(price, 'GBP')
            self.assertEqual(converted_price.value, 1.50)
            self.assertEqual(converted_price.currency, 'GBP')

    def test_price(self):
        """Test :py:class:``exchange.conversion.Price``"""
        from exchange.conversion import Price
        with patch('exchange.conversion.ExchangeRates') as exchange_rates:
            exchange_rates.get_instance.return_value = \
                {'USD': {'GBP': 0.5}}
            price = Price(3, 'USD')
            converted_price = price.convert('GBP')
            self.assertEqual(converted_price.value, 1.50)
            self.assertEqual(converted_price.currency, 'GBP')

    def test_exchangerates(self):
        """Test :py:class:``exchange.conversion.ExchangeRates``"""
        from exchange.conversion import ExchangeRates
        from exchange.models import Currency, ExchangeRate
        usd = Currency.objects.create(code='USD')
        gbp = Currency.objects.create(code='GBP')
        afn = Currency.objects.create(code='AFN')

        ExchangeRate.objects.create(source=usd, target=gbp, rate='2.00')
        ExchangeRate.objects.create(source=usd, target=afn, rate='3.00')

        rates = ExchangeRates.get_instance()
        rates.populate()
        self.assertIn('USD', rates)
        self.assertIn('GBP', rates['USD'])
        self.assertEqual(rates['USD']['GBP'], 2.00)
        self.assertIn('AFN', rates['USD'])
        self.assertEqual(rates['USD']['AFN'], 3.00)
        rates2 = ExchangeRates.get_instance()
        self.assertEqual(rates, rates2)
        rates.clear()
        self.assertEqual(len(rates), 0)
