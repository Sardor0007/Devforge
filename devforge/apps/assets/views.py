from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Asset, AssetCategory, CartItem, PurchasedAsset
from .forms import AssetUploadForm


def asset_list_view(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    price_filter = request.GET.get('price', '')
    fmt = request.GET.get('format', '')

    is_moderator = request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'developer'
    )
    pending_count = Asset.objects.filter(status='pending').count() if is_moderator else 0

    # Private Offer (only_for_user) and public approval logic
    if request.user.is_authenticated:
        assets = Asset.objects.filter(
            Q(only_for_user__isnull=True) | Q(only_for_user=request.user) | Q(creator=request.user),
            is_approved=True,
            status='approved'
        ).select_related('creator', 'category')
    else:
        assets = Asset.objects.filter(
            only_for_user__isnull=True,
            is_approved=True,
            status='approved'
        ).select_related('creator', 'category')

    if query:
        assets = assets.filter(
            Q(title__icontains=query) | Q(tags__name__icontains=query) | Q(description__icontains=query)
        )
    if category:
        assets = assets.filter(category__slug=category)
    if price_filter == 'free':
        assets = assets.filter(price=0)
    elif price_filter == 'paid':
        assets = assets.filter(price__gt=0)
    if fmt:
        assets = assets.filter(format=fmt)

    from django.core.paginator import Paginator
    categories = AssetCategory.objects.all()
    paginator  = Paginator(assets.order_by('-created_at'), 12)
    page_obj   = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'assets/list.html', {
        'assets': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'query': query,
        'format_choices': Asset.FORMAT_CHOICES,
        'is_moderator': is_moderator,
        'pending_count': pending_count,
    })


def asset_detail_view(request, pk):
    asset = get_object_or_404(Asset.objects.select_related('creator', 'category'), pk=pk)

    is_moderator = request.user.is_authenticated and (
        request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'developer'
    )

    # If unapproved, only creator and moderators can view
    if not asset.is_approved:
        if not request.user.is_authenticated or (asset.creator != request.user and not is_moderator):
            messages.info(request, "Ushbu aktiv hozirda moderator ko'rib chiqish jarayonida (kutilmoqda).")
            return redirect('asset_list')

    # Private Offer (only_for_user) logic
    if asset.only_for_user:
        if not request.user.is_authenticated:
            messages.error(request, "Ushbu aktiv faqat maxsus foydalanuvchi uchun mo'ljallangan.")
            return redirect('asset_list')
        if asset.only_for_user != request.user and asset.creator != request.user and not is_moderator:
            messages.error(request, "Ushbu aktiv faqat maxsus foydalanuvchi uchun mo'ljallangan.")
            return redirect('asset_list')

    related = Asset.objects.filter(
        category=asset.category, is_approved=True, status='approved'
    ).exclude(pk=pk)[:4]

    is_liked = request.user.is_authenticated and asset.likes.filter(pk=request.user.pk).exists()

    is_purchased = False
    is_in_cart = False
    user_projects = None
    if request.user.is_authenticated:
        is_purchased = PurchasedAsset.objects.filter(user=request.user, asset=asset).exists()
        is_in_cart = CartItem.objects.filter(user=request.user, asset=asset).exists()
        from apps.studio.models import StudioProject
        user_projects = StudioProject.objects.filter(owner=request.user)

    return render(request, 'assets/detail.html', {
        'asset': asset,
        'related': related,
        'is_liked': is_liked,
        'is_purchased': is_purchased,
        'is_in_cart': is_in_cart,
        'user_projects': user_projects,
        'is_moderator': is_moderator,
    })


@login_required
def cart_list_view(request):
    items = CartItem.objects.filter(user=request.user).select_related('asset', 'asset__creator', 'asset__category')
    total = sum(item.asset.price for item in items)
    return render(request, 'assets/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def add_to_cart_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if asset.is_free:
        messages.info(request, "Ushbu aktiv tekin, uni to'g'ridan-to'g'ri yuklab olishingiz mumkin.")
        return redirect('asset_detail', pk=pk)
    
    if asset.creator == request.user:
        messages.warning(request, "O'zingiz yaratgan aktivni sotib ololmaysiz.")
        return redirect('asset_detail', pk=pk)

    if PurchasedAsset.objects.filter(user=request.user, asset=asset).exists():
        messages.info(request, "Siz ushbu aktivni allaqachon sotib olgansiz.")
        return redirect('asset_detail', pk=pk)

    CartItem.objects.get_or_create(user=request.user, asset=asset)
    messages.success(request, f"'{asset.title}' savatga qo'shildi.")
    return redirect('cart_list')


@login_required
def remove_from_cart_view(request, pk):
    item = get_object_or_404(CartItem, pk=pk, user=request.user)
    item.delete()
    return redirect('cart_list')


@login_required
def checkout_view(request):
    from decimal import Decimal
    from django.db import transaction
    from django.db.models import F

    if request.method != 'POST':
        return redirect('cart_list')

    user = request.user
    items = CartItem.objects.filter(user=user).select_related('asset', 'asset__creator')
    if not items.exists():
        return redirect('asset_list')

    unpurchased_items = [
        item for item in items
        if not PurchasedAsset.objects.filter(user=user, asset=item.asset).exists()
    ]

    if not unpurchased_items:
        items.delete()
        messages.info(request, "Barcha aktivlar allaqachon sotib olingan edi.")
        return redirect('asset_list')

    total_cost = sum((item.asset.price for item in unpurchased_items), Decimal('0'))

    if user.balance < total_cost:
        messages.error(request, f"Hisobingizda mablag' yetarli emas. Kerak: ${total_cost}, mavjud: ${user.balance}.")
        return redirect('cart_list')

    try:
        with transaction.atomic():
            from apps.accounts.models import User as UserModel, Transaction
            UserModel.objects.filter(pk=user.pk).update(balance=F('balance') - total_cost)
            
            # Record withdrawal
            Transaction.objects.create(
                user=user,
                amount=-total_cost,
                transaction_type='purchase',
                description=f"{len(unpurchased_items)} ta aktiv sotib olindi"
            )

            for item in unpurchased_items:
                asset = item.asset
                PurchasedAsset.objects.get_or_create(
                    user=user,
                    asset=asset,
                    defaults={'price_paid': asset.price}
                )
                UserModel.objects.filter(pk=asset.creator.pk).update(balance=F('balance') + asset.price)
                
                # Record income for creator
                Transaction.objects.create(
                    user=asset.creator,
                    amount=asset.price,
                    transaction_type='sale',
                    description=f"Aktiv sotildi: {asset.title}"
                )

            items.delete()
    except Exception:
        messages.error(request, "To'lovda xatolik yuz berdi. Qayta urinib ko'ring.")
        return redirect('cart_list')

    user.refresh_from_db()
    messages.success(request, f"✅ To'lov muvaffaqiyatli! ${total_cost} yechib olindi.")
    return redirect('asset_list')


@login_required
def cart_count_api(request):
    count = CartItem.objects.filter(user=request.user).count()
    return JsonResponse({'count': count})


@login_required
def asset_upload_view(request):
    from django.utils import timezone
    from datetime import timedelta
    last_month = timezone.now() - timedelta(days=30)
    created_count = Asset.objects.filter(creator=request.user, created_at__gte=last_month).count()
    limit = request.user.get_upload_limit()

    if created_count >= limit:
        messages.error(request, f"Sizning oylik yuklash limitingiz ({limit} ta) tugagan. Pro yoki Studio obunaga o'ting.")
        return redirect('subscription_plans')

    if request.method == 'POST':
        form = AssetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.creator = request.user
            asset.is_approved = False
            asset.status = 'pending'
            asset.save()
            
            # Log Activity & Award XP
            try:
                from apps.accounts.models import UserActivity
                UserActivity.log_activity(request.user, 'asset')
            except Exception as e:
                print(f"Failed to log asset upload activity: {e}")

            messages.success(
                request,
                f"'{asset.title}' aktivi muvaffaqiyatli yuklandi! 🛡️ U hozirda moderator ko'rib chiqish navbatida. Tasdiqlangach, platformada e'lon qilinadi."
            )
            return redirect('my_assets')
    else:
        form = AssetUploadForm()
    return render(request, 'assets/upload.html', {'form': form})


@login_required
def asset_like_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    if asset.likes.filter(pk=request.user.pk).exists():
        asset.likes.remove(request.user)
    else:
        asset.likes.add(request.user)
        try:
            from apps.notifications.service import notify_asset_liked
            notify_asset_liked(asset, request.user)
        except Exception:
            pass
    return redirect('asset_detail', pk=pk)


@login_required
def asset_download_view(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    can_download = (
        asset.is_free or
        asset.creator == request.user or
        PurchasedAsset.objects.filter(user=request.user, asset=asset).exists()
    )

    if not can_download:
        messages.error(request, "Ushbu aktivni yuklab olish uchun avval uni sotib olishingiz kerak.")
        return redirect('asset_detail', pk=pk)

    if not asset.file:
        messages.error(request, "Fayl topilmadi. Muallif bilan bog'laning.")
        return redirect('asset_detail', pk=pk)

    asset.downloads += 1
    asset.save(update_fields=['downloads'])
    try:
        from apps.notifications.service import notify_asset_downloaded
        notify_asset_downloaded(asset, request.user)
    except Exception:
        pass

    from django.http import FileResponse
    try:
        return FileResponse(
            asset.file.open('rb'),
            as_attachment=True,
            filename=asset.file.name.split('/')[-1]
        )
    except Exception:
        messages.error(request, "Faylni yuklashda xatolik yuz berdi.")
        return redirect('asset_detail', pk=pk)


@login_required
def asset_buy_direct(request, pk):
    from decimal import Decimal
    from django.db import transaction
    from django.db.models import F

    asset = get_object_or_404(Asset, pk=pk)
    if asset.is_free:
        return redirect('asset_download', pk=pk)

    if asset.creator == request.user:
        messages.warning(request, "O'zingiz yaratgan aktivni sotib ololmaysiz.")
        return redirect('asset_detail', pk=pk)

    if PurchasedAsset.objects.filter(user=request.user, asset=asset).exists():
        messages.info(request, "Siz ushbu aktivni allaqachon sotib olgansiz.")
        return redirect('asset_download', pk=pk)

    user = request.user
    price = asset.price

    if user.balance < price:
        messages.error(
            request,
            f"Hisobingizda mablag' yetarli emas. Kerak: ${price}, mavjud: ${user.balance}."
        )
        return redirect('subscription_plans')

    try:
        with transaction.atomic():
            from apps.accounts.models import User as UserModel, Transaction
            updated = UserModel.objects.filter(
                pk=user.pk, balance__gte=price
            ).update(balance=F('balance') - price)

            if not updated:
                messages.error(request, "Hisobingizda mablag' yetarli emas.")
                return redirect('asset_detail', pk=pk)

            # Record withdrawal
            Transaction.objects.create(
                user=user,
                amount=-price,
                transaction_type='purchase',
                description=f"Aktiv sotib olindi: {asset.title}"
            )

            UserModel.objects.filter(pk=asset.creator.pk).update(balance=F('balance') + price)
            
            # Record income for creator
            Transaction.objects.create(
                user=asset.creator,
                amount=price,
                transaction_type='sale',
                description=f"Aktiv sotildi: {asset.title}"
            )

            PurchasedAsset.objects.get_or_create(
                user=user,
                asset=asset,
                defaults={'price_paid': price}
            )
            CartItem.objects.filter(user=user, asset=asset).delete()

    except Exception:
        messages.error(request, "To'lovda xatolik yuz berdi. Qayta urinib ko'ring.")
        return redirect('asset_detail', pk=pk)

    user.refresh_from_db()
    messages.success(request, f"✅ '{asset.title}' muvaffaqiyatli sotib olindi! 🎉")
    return redirect('asset_download', pk=pk)


# ──────────────────────────────────────────────────────────────────────────────
# MODERATSIYA PANELI (Admin & Developerlar uchun)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def asset_moderation_list_view(request):
    """Admin va Developerlar uchun barcha aktivlarni tekshirish va tasdiqlash paneli"""
    is_moderator = request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'developer'
    if not is_moderator:
        messages.error(request, "Ushbu bo'limga faqat moderatorlar va developerlar kira oladi.")
        return redirect('asset_list')

    status_filter = request.GET.get('status', 'pending')
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    base_qs = Asset.objects.all().select_related('creator', 'category', 'reviewed_by')

    if query:
        base_qs = base_qs.filter(Q(title__icontains=query) | Q(creator__username__icontains=query))
    if category_slug:
        base_qs = base_qs.filter(category__slug=category_slug)

    pending_qs = base_qs.filter(status='pending').order_by('-created_at')
    approved_qs = base_qs.filter(status='approved').order_by('-reviewed_at', '-created_at')
    rejected_qs = base_qs.filter(status='rejected').order_by('-reviewed_at', '-created_at')

    counts = {
        'pending': Asset.objects.filter(status='pending').count(),
        'approved': Asset.objects.filter(status='approved').count(),
        'rejected': Asset.objects.filter(status='rejected').count(),
    }

    if status_filter == 'approved':
        active_qs = approved_qs
    elif status_filter == 'rejected':
        active_qs = rejected_qs
    else:
        active_qs = pending_qs
        status_filter = 'pending'

    from django.core.paginator import Paginator
    categories = AssetCategory.objects.all()
    paginator = Paginator(active_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'assets/moderation.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'counts': counts,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })


@login_required
def asset_moderation_approve_view(request, pk):
    """Aktivni tasdiqlash (Approve)"""
    is_moderator = request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'developer'
    if not is_moderator:
        messages.error(request, "Ruxsat etilmagan amal.")
        return redirect('asset_list')

    asset = get_object_or_404(Asset, pk=pk)
    from django.utils import timezone
    asset.is_approved = True
    asset.status = 'approved'
    asset.rejection_reason = None
    asset.reviewed_by = request.user
    asset.reviewed_at = timezone.now()
    asset.save()

    # Muallifga bildirishnoma yuborish
    try:
        from apps.notifications.models import Notification
        from django.urls import reverse
        Notification.objects.create(
            recipient=asset.creator,
            sender=request.user,
            notif_type='asset_approved',
            title="Aktiv tasdiqlandi! 🎉",
            message=f"Tabriklaymiz! Sizning '{asset.title}' nomli aktivingiz administrator tomonidan tasdiqlandi va platformada ommaga e'lon qilindi.",
            link=reverse('asset_detail', args=[asset.pk])
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

    messages.success(request, f"'{asset.title}' aktivi muvaffaqiyatli tasdiqlandi va ommaga e'lon qilindi!")
    return redirect(request.META.get('HTTP_REFERER') or 'asset_moderation_list')


@login_required
def asset_moderation_reject_view(request, pk):
    """Aktivni bekor qilish / rad etish (Reject)"""
    is_moderator = request.user.is_staff or request.user.is_superuser or getattr(request.user, 'role', '') == 'developer'
    if not is_moderator:
        messages.error(request, "Ruxsat etilmagan amal.")
        return redirect('asset_list')

    asset = get_object_or_404(Asset, pk=pk)
    reason = request.POST.get('reason', '').strip()
    if not reason:
        reason = "Format, fayl butunligi yoki sifat talablariga mos kelmadi."

    from django.utils import timezone
    asset.is_approved = False
    asset.status = 'rejected'
    asset.rejection_reason = reason
    asset.reviewed_by = request.user
    asset.reviewed_at = timezone.now()
    asset.save()

    # Muallifga bildirishnoma yuborish
    try:
        from apps.notifications.models import Notification
        from django.urls import reverse
        Notification.objects.create(
            recipient=asset.creator,
            sender=request.user,
            notif_type='asset_rejected',
            title="Aktiv rad etildi ⚠️",
            message=f"Sizning '{asset.title}' nomli aktivingiz rad etildi. Sababi: {reason}",
            link=reverse('my_assets')
        )
    except Exception as e:
        print(f"Failed to send notification: {e}")

    messages.warning(request, f"'{asset.title}' aktivi rad etildi.")
    return redirect(request.META.get('HTTP_REFERER') or 'asset_moderation_list')


@login_required
def my_assets_view(request):
    """Foydalanuvchining shaxsiy aktivlari va ularning holati"""
    user_assets = Asset.objects.filter(creator=request.user).select_related('category').order_by('-created_at')

    counts = {
        'all': user_assets.count(),
        'pending': user_assets.filter(status='pending').count(),
        'approved': user_assets.filter(status='approved').count(),
        'rejected': user_assets.filter(status='rejected').count(),
    }

    status_filter = request.GET.get('status', 'all')
    if status_filter in ('pending', 'approved', 'rejected'):
        user_assets = user_assets.filter(status=status_filter)

    from django.core.paginator import Paginator
    paginator = Paginator(user_assets, 12)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'assets/my_assets.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'counts': counts,
    })

