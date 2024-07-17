from celery import shared_task
from .models import BuyOffer, SellOffer, CustomUser,Transaction
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

@shared_task
def execute_transactions():
    now = timezone.now()
    try:
        buy_offers = BuyOffer.objects.filter(dateLimit__gt=now, actual=True).order_by('-maxPrice')
        sell_offers = SellOffer.objects.filter(dateLimit__gt=now, actual=True).order_by('minPrice')

        for buy_offer in buy_offers:
            for sell_offer in sell_offers:
                if (buy_offer.company == sell_offer.company and
                    buy_offer.amount > 0 and 
                    sell_offer.amount > 0 and 
                    buy_offer.maxPrice >= sell_offer.minPrice):
                    amount_to_trade = min(buy_offer.amount, sell_offer.amount)
                    total_price = amount_to_trade * buy_offer.maxPrice

                    buyer = buy_offer.user
                    seller = sell_offer.user

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

                        Transaction.objects.create(
                            buyOffer=buy_offer,
                            sellOffer=sell_offer,
                            amount=amount_to_trade,
                            price=buy_offer.maxPrice,
                            total_price=total_price,
                            transactionDate=timezone.now()
                        )
                    else:
                        continue
    except Exception as e:
        logger.error(f"Error executing transactions: {e}")
        raise e
