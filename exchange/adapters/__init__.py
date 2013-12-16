import logging
from decimal import Decimal

from exchange.models import Currency, ExchangeRate

from exchange.utils import update_many, insert_many

logger = logging.getLogger(__name__)


class BaseAdapter(object):
    """Base adapter class provides an interface for updating currency and
    exchange rate models

    """
    def update(self):
        """Actual update process goes here using auxialary ``get_currencies``
        and ``get_exchangerates`` methods. This method creates or updates
        corresponding ``Currency`` and ``ExchangeRate`` models

        """
        currencies = self.get_currencies()
        for code, name in currencies:
            _, created = Currency.objects.get_or_create(
                code=code, defaults={'name': name})
            if created:
                logger.info('currency: %s created', code)

        pairs = set(ExchangeRate.objects.values_list('source__code',
                                                     'target__code'))
        usd_exchange_rates = dict(self.get_exchangerates('USD'))

        updates = []
        inserts = []
        currencies = list(Currency.objects.all())
        for source in currencies:
            for target in currencies:
                rate = self._get_rate_through_usd(source.code,
                                                  target.code,
                                                  usd_exchange_rates)

                exchange_rate = ExchangeRate(source=source,
                                             target=target,
                                             rate=rate)

                if (source.code, target.code) in pairs:
                    updates.append(exchange_rate)
                    logger.debug('exchange rate updated %s/%s=%s'
                                 % (source, target, rate))
                else:
                    inserts.append(exchange_rate)
                    logger.debug('exchange rate created %s/%s=%s'
                                 % (source, target, rate))

            logger.info('exchange rates updated for %s' % source.code)
        logger.info("Updating %s rows" % len(updates))
        update_many(updates)
        logger.info("Inserting %s rows" % len(inserts))
        insert_many(inserts)
        logger.info('saved rates to db')

    def _get_rate_through_usd(self, source, target, usd_rates):
        # from: https://openexchangerates.org/documentation#how-to-use
        # gbp_hkd = usd_hkd * (1 / usd_gbp)
        usd_source = usd_rates[source]
        usd_target = usd_rates[target]
        rate = usd_target * (Decimal(1.0) / usd_source)
        rate = rate.quantize(Decimal('0.123456'))  # round to 6 decimal places
        return rate

    def get_currencies(self):
        """Subclasses must implement this to provide all currency data

        :returns: currency tuples ``[(currency_code, currency_name),]``
        :rtype: list

        """
        raise NotImplementedError()

    def get_exchangerates(self, base):
        """Subclasses must implement this to provide corresponding exchange
        rates for given base currency

        :returns: exchange rate tuples ``[(currency_code, rate),]``
        :rtype: list

        """
        raise NotImplementedError()
