from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, Order, Review
from .forms import ServiceForm, OrderForm, ReviewForm


# ─── VIEWS ───────────────────────────────────────────────────────────────────

def service_list_view(request):
    category = request.GET.get('category', '')
    query = request.GET.get('q', '')
    services = Service.objects.filter(is_active=True).select_related('seller')
    
    if category:
        services = services.filter(category=category)
    if query:
        from django.db.models import Q
        services = services.filter(Q(title__icontains=query) | Q(description__icontains=query))
    
    from django.core.paginator import Paginator
    paginator = Paginator(services.order_by('-created_at'), 12)
    page_obj  = paginator.get_page(request.GET.get('page', 1))
    
    return render(request, 'marketplace/list.html', {
        'services': page_obj, 
        'page_obj': page_obj,
        'category_choices': Service.CATEGORY_CHOICES,
        'current_category': category,
        'query': query,
    })


def service_detail_view(request, pk):
    service = get_object_or_404(Service.objects.select_related('seller'), pk=pk, is_active=True)
    reviews = service.reviews.select_related('reviewer')
    order_form = OrderForm()
    review_form = ReviewForm()
    
    has_ordered = request.user.is_authenticated and Order.objects.filter(
        buyer=request.user, service=service, status='completed'
    ).exists()
    
    has_reviewed = request.user.is_authenticated and Review.objects.filter(
        reviewer=request.user, service=service
    ).exists()
    
    return render(request, 'marketplace/detail.html', {
        'service': service,
        'reviews': reviews,
        'order_form': order_form,
        'review_form': review_form,
        'has_ordered': has_ordered,
        'has_reviewed': has_reviewed,
    })


@login_required
def service_create_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save(commit=False)
            service.seller = request.user
            service.save()
            messages.success(request, "Xizmat e'lon qilindi!")
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, 'marketplace/create.html', {'form': form})


@login_required
def order_create_view(request, pk):
    from decimal import Decimal
    service = get_object_or_404(Service, pk=pk, is_active=True)
    if service.seller == request.user:
        messages.error(request, "O'z xizmatingizga buyurtma bera olmaysiz.")
        return redirect('service_detail', pk=pk)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Balans tekshiruvi
            price = service.price
            if request.user.balance < price:
                messages.error(
                    request,
                    f"Hisobingizda mablag' yetarli emas. Kerak: ${price}, "
                    f"Sizda: ${request.user.balance}."
                )
                return redirect('subscription_plans')

            import datetime
            order = form.save(commit=False)
            order.buyer = request.user
            order.service = service
            order.amount = price
            order.deadline = datetime.date.today() + datetime.timedelta(days=service.delivery_days)
            order.save()

            # Xaridordan pul yechish (Escrow sifatida ushlab turiladi)
            request.user.balance -= price
            request.user.save(update_fields=['balance'])

            try:
                from apps.notifications.service import notify_order_placed
                notify_order_placed(order)
            except Exception:
                pass

            messages.success(request, f"Buyurtmangiz qabul qilindi! ${price} balansingizdan yechildi.")
            return redirect('order_list')

    return redirect('service_detail', pk=pk)


@login_required
def order_list_view(request):
    orders = Order.objects.filter(buyer=request.user).select_related('service', 'service__seller')
    my_service_orders = Order.objects.filter(
        service__seller=request.user
    ).select_related('buyer', 'service')
    
    return render(request, 'marketplace/orders.html', {
        'orders': orders,
        'my_service_orders': my_service_orders,
    })


@login_required
def order_confirm_view(request, pk):
    order = get_object_or_404(Order, pk=pk, service__seller=request.user)
    if order.status == 'pending':
        order.status = 'active'
        order.save()

        # Sotuvchiga pul o'tkazish
        seller = request.user
        seller.balance += order.amount
        seller.save(update_fields=['balance'])

        messages.success(request, f"Buyurtma tasdiqlandi! ${order.amount} balansingizga o'tkazildi.")

        # Suhbatni boshlash
        try:
            from apps.messaging.views import Conversation
            conv = Conversation.get_or_create_between(request.user, order.buyer)
            return redirect('conversation', conv_id=conv.pk)
        except Exception:
            pass

    return redirect('order_list')


@login_required
def review_create_view(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.service = service
            review.reviewer = request.user
            review.save()
            
            try:
                from apps.notifications.service import notify_review_received
                notify_review_received(review)
            except Exception:
                pass
                
            messages.success(request, "Sharh qoldirildi!")
            
    return redirect('service_detail', pk=pk)
