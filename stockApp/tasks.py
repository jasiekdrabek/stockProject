from celery import shared_task, group
from .models import BuyOffer, SellOffer, CustomUser,Transaction, Company, Stock, StockRate
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

@shared_task
def execute_transactions(company_ids):
    try:
        for company_id in company_ids:
            buy_offers = BuyOffer.objects.filter(company_id__in=company_ids, actual=True).order_by('-maxPrice')
            sell_offers = SellOffer.objects.filter(company_id__in=company_ids, actual=True).order_by('minPrice')
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
                        total_price = amount_to_trade * buy_offer.maxPrice
                        if buyer.money >= total_price:
                            buy_offer.amount -= amount_to_trade
                            sell_offer.amount -= amount_to_trade

                            if buy_offer.amount == 0:
                                buy_offer.actual = False
                            if sell_offer.amount == 0:
                                sell_offer.actual = False
                            buy_offer.save()
                            sell_offer.save()

                            buyer.money -= total_price
                            seller.money += total_price
                            buyer.save()
                            seller.save()
                            sell_stock = Stock.objects.get(user=sell_offer.user, company_id=company_id)
                            sell_stock.amount -= amount_to_trade
                            sell_stock.save()

                            # Aktualizacja akcji kupującego
                            buy_stock, created = Stock.objects.get_or_create(user=buy_offer.user, company_id=company_id)
                            buy_stock.amount += amount_to_trade
                            buy_stock.save()
                            Transaction.objects.create(
                                buyOffer=buy_offer,
                                sellOffer=sell_offer,
                                amount=amount_to_trade,
                                price=buy_offer.maxPrice,
                                total_price=total_price
                            )
                        else:
                            continue
    except Exception as e:
        logger.error(f"Error executing transactions: {e}")
        raise e

@shared_task
def schedule_transactions():
    companies = Company.objects.all()
    num_companies = companies.count()
    group_size = 1 + num_companies // 4  # Assuming you want 4 groups, adjust as needed

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
                updated_rate = (last_rate + new_average_rate) / 2
                last_stock_rate.actual = False
                last_stock_rate.save()
            except StockRate.DoesNotExist:
                # Jeśli nie ma ostatniego rate'u, ustaw nową średnią jako aktualną wartość
                updated_rate = new_average_rate
            
            # Utwórz nowy `StockRate`
            StockRate.objects.create(
                company_id=company_id,
                rate=updated_rate,
                date_inc=timezone.now()
            )