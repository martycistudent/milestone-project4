from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.conf import settings
import stripe
from django.contrib.auth.decorators import login_required
from .forms import OrderForm, MakePaymentForm
from django.utils import timezone
from products.models import Game
from .models import OrderLineItem
from django.contrib import messages


stripe.api_key = settings.STRIPE_SECRET


@login_required()
def checkout(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)
        payment_form = MakePaymentForm(request.POST)

        if order_form.is_valid() and payment_form.is_valid():
            order = order_form.save(commit=False)
            order.date = timezone.now()
            order.save()

            cart = request.session.get('cart', {})
            total = 0
            for id, quantity in cart.items():
                game = get_object_or_404(Game, pk=id)
                if game.sale_price:
                    total += quantity * game.sale_price
                else:
                    total += quantity * game.price

                order_line_item = OrderLineItem(
                    order=order,
                    game=game,
                    quantity=quantity
                )
                order_line_item.save()

            try:
                customer = stripe.Charge.create(
                    amount=int(total * 100),
                    currency="EUR",
                    description=request.user.email,
                    card=payment_form.cleaned_data['stripe_id'],
                )
                if customer.paid:
                    messages.error(request, "You have successfully paid")
                    request.session['cart'] = {}
                    return redirect(reverse('index'))
                else:
                    messages.error(request, "Unable to make card payment")

            except stripe.error.CardError:
                messages.error(request, "Your card was declined!")

        else:
            print(payment_form.errors)
            messages.error(request, "We were unable to take payment with that card!")
    else:
        payment_form = MakePaymentForm()
        order_form = OrderForm()

    return render(request, 'checkout/checkout.html', {'order_form': order_form, 'payment_form': payment_form, 'publishable': settings.STRIPE_PUBLISHABLE})
