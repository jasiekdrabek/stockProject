
import datetime
import math
import time
from celery import shared_task, group
from .models import BuyOffer, SellOffer, BalanceUpdate,Transaction, Company, Stock, StockRate, TradeLog
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@shared_task
def execute_transactions(company_ids):
    try:
        database_time = 0
        number_of_sell_offers = 0
        number_of_buy_offers = 0
        start_time = time.time()
        for company_id in company_ids:
            db_start_time = time.time()
            buy_offers = BuyOffer.objects.filter(company_id=company_id, actual=True).order_by('-maxPrice')
            sell_offers = SellOffer.objects.filter(company_id=company_id, actual=True).order_by('minPrice')
            db_end_time = time.time()
            database_time += db_end_time - db_start_time
            number_of_buy_offers += buy_offers.count()
            number_of_sell_offers += sell_offers.count()
            if number_of_sell_offers == 0 and number_of_buy_offers == 0:
                continue
            for buy_offer in buy_offers:
                for sell_offer in sell_offers:
                    buyer = buy_offer.user
                    seller = sell_offer.user
                    if (buy_offer.company == sell_offer.company and
                        buy_offer.amount > 0 and 
                        sell_offer.amount > 0 and 
                        buy_offer.maxPrice >= sell_offer.minPrice and
                        seller != buyer):
                        amount_to_trade = min(buy_offer.amount, sell_offer.amount)
                        price = (buy_offer.maxPrice + sell_offer.minPrice) /2
                        total_price = round(amount_to_trade * price,2)
                        with transaction.atomic():
                            if buyer.money >= total_price:
                                buy_offer.amount -= amount_to_trade
                                sell_offer.amount -= amount_to_trade

                                if buy_offer.amount == 0:
                                    buy_offer.actual = False
                                if sell_offer.amount == 0:
                                    sell_offer.actual = False
                                db_start_time = time.time()    
                                buy_offer.save()
                                sell_offer.save()
                                db_end_time = time.time()
                                database_time += db_end_time - db_start_time

                                # Aktualizacja pieniędzy dla kupującego i sprzedającego
                                 # Oblicz zmiany w saldzie
                                buyer_money_change = -total_price
                                buyer_money_after_transactions_change = -(total_price - amount_to_trade * buy_offer.maxPrice)
                                seller_money_change = total_price
                                seller_money_after_transactions_change = total_price

                                # Tworzenie wpisu BalanceUpdate dla kupującego
                                db_start_time = time.time() 
                                BalanceUpdate.objects.create(
                                    user=buyer,
                                    change_amount=buyer_money_change,
                                    change_type='money'
                                )
                                BalanceUpdate.objects.create(
                                    user=buyer,
                                    change_amount=buyer_money_after_transactions_change,
                                    change_type='moneyAfterTransactions'
                                )

                                # Tworzenie wpisu BalanceUpdate dla sprzedającego
                                BalanceUpdate.objects.create(
                                    user=seller,
                                    change_amount=seller_money_change,
                                    change_type='money'
                                )
                                BalanceUpdate.objects.create(
                                    user=seller,
                                    change_amount=seller_money_after_transactions_change,
                                    change_type='moneyAfterTransactions'
                                )

                                # Aktualizacja akcji kupującego; sprzedający ma zabrane w momencie tworzenia oferty, aby nie mógł utworzyć nieskończenie wiele ofert.
                                buy_stock, created = Stock.objects.get_or_create(user=buy_offer.user, company_id=company_id)
                                db_end_time = time.time()
                                database_time += db_end_time - db_start_time
                                buy_stock.amount += amount_to_trade
                                db_start_time = time.time() 
                                buy_stock.save()
                                Transaction.objects.create(
                                    buyOffer=buy_offer,
                                    sellOffer=sell_offer,
                                    amount=amount_to_trade,
                                    price=price,
                                    total_price=total_price
                                )
                                db_end_time = time.time()
                                database_time += db_end_time - db_start_time
                            else:
                                continue
        if number_of_sell_offers == 0 and number_of_buy_offers == 0:
            return company_ids               
        # Pomiar końcowy czasu aplikacji
        end_time = time.time()

        # Obliczenie czasu aplikacji i czasu bazy danych
        application_time = end_time - start_time

            # Zapis do modelu TradeLog
        TradeLog.objects.using('test').create(
            application_time=application_time,
            database_time=database_time,
            number_of_sell_offers=number_of_sell_offers,
            number_of_buy_offers=number_of_buy_offers,
            timestamp = datetime.datetime.now(),
            company_ids = company_ids
            )                            
        return company_ids
    except Exception as e:
        logger.error(f"Error executing transactions: {e}")
        raise e

@shared_task
def schedule_transactions():
    companies = Company.objects.all()
    num_companies = companies.count()
    group_size = 1 + num_companies // max(1,math.ceil(math.sqrt(num_companies)))  # Assuming you want 4 groups, adjust as needed

    company_groups = [companies[i:i + group_size] for i in range(0, num_companies, group_size)]

    
    tasks = group(execute_transactions.s([company.id for company in group]) for group in company_groups)
    tasks.apply_async()

@shared_task
def update_stock_rates():
    companies = StockRate.objects.values_list('company', flat=True).distinct()
    
    for company_id in companies:
        # Obliczanie średniej ceny z ofert kupna i sprzedaży
        buy_offers = BuyOffer.objects.filter(company_id=company_id, actual=True)
        sell_offers = SellOffer.objects.filter(company_id=company_id, actual=True)
        
        buy_prices = buy_offers.values_list('maxPrice', flat=True)
        sell_prices = sell_offers.values_list('minPrice', flat=True)
        
        all_prices = list(buy_prices) + list(sell_prices)
        
        if all_prices:
            new_average_rate = sum(all_prices) / len(all_prices)
            
            # Pobierz ostatni `StockRate` dla danej firmy
            try:
                last_stock_rate = StockRate.objects.filter(company_id=company_id, actual=True).latest('date_inc')
                last_rate = last_stock_rate.rate
                # Oblicz średnią z ostatniego rate'u i nowej średniej
                updated_rate = (last_rate + sum(all_prices)) / (len(all_prices) + 1)
                last_stock_rate.actual = False
                last_stock_rate.save()
            except StockRate.DoesNotExist:
                # Jeśli nie ma ostatniego rate'u, ustaw nową średnią jako aktualną wartość
                updated_rate = new_average_rate
            
            # Utwórz nowy `StockRate`
            StockRate.objects.create(
                company_id=company_id,
                rate=updated_rate,
                date_inc=datetime.datetime.now()
            )

@shared_task
def process_balance_updates():
    updates = BalanceUpdate.objects.all()
    
    with transaction.atomic():
        for update in updates:
            user = update.user
            if update.change_type == 'money':
                user.money += update.change_amount
            elif update.change_type == 'moneyAfterTransactions':
                user.moneyAfterTransations += update.change_amount
            user.save()
        BalanceUpdate.objects.filter(id__in=[update.id for update in updates]).delete()

@shared_task
def expire_offers():
    now = datetime.datetime.now()

    # Znajdowanie i aktualizowanie przeterminowanych ofert kupna
    expired_buy_offers = BuyOffer.objects.filter(actual=True, dateLimit__lt=now)
    for offer in expired_buy_offers:
        buyer = offer.user
        buyer_money_after_transactions_change = offer.amount * offer.maxPrice
        BalanceUpdate.objects.create(
                                    user=buyer,
                                    change_amount=buyer_money_after_transactions_change,
                                    change_type='moneyAfterTransactions'
                                )
        offer.actual = False
        offer.save()

    # Znajdowanie i aktualizowanie przeterminowanych ofert sprzedaży
    expired_sell_offers = SellOffer.objects.filter(actual=True, dateLimit__lt=now)
    for offer in expired_sell_offers:
        seller = offer.user
        stock = Stock.objects.get(user=seller, company=offer.company)
        stock.amount += offer.amount
        offer.actual = False
        offer.save()
        stock.save()