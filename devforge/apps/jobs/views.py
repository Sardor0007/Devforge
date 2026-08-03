from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Job, Proposal, EscrowPayment, Delivery, Dispute
from apps.projects.models import Project


# ── JOB VIEWS ─────────────────────────────────────────────────────────────────

def job_list_view(request):
    """Barcha ochiq va ommaviy ishlarni ko'rish"""
    # open + funded ishlarini ko'rsatish (funded bo'lsa ham yangi ariza yo'q, lekin ko'rish mumkin)
    jobs = Job.objects.filter(visibility='public').exclude(
        status__in=['approved', 'completed', 'cancelled']
    ).select_related('client')

    query = request.GET.get('q', '')
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(description__icontains=query))

    budget_filter = request.GET.get('budget', '')
    if budget_filter == 'low':
        jobs = jobs.filter(budget__lt=500000)
    elif budget_filter == 'mid':
        jobs = jobs.filter(budget__gte=500000, budget__lt=2000000)
    elif budget_filter == 'high':
        jobs = jobs.filter(budget__gte=2000000)

    return render(request, 'jobs/list.html', {'jobs': jobs, 'query': query, 'budget_filter': budget_filter})


@login_required
def job_create_view(request):
    """Yangi ish e'loni yaratish"""
    if request.method == 'POST':
        from decimal import Decimal
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        budget_raw = request.POST.get('budget', '0')
        visibility = request.POST.get('visibility', 'public')
        deadline = request.POST.get('deadline')
        project_id = request.POST.get('project')

        if not title or not description:
            messages.error(request, "Sarlavha va tavsif majburiy!")
            user_projects = Project.objects.filter(creator=request.user)
            return render(request, 'jobs/create.html', {'user_projects': user_projects})

        try:
            budget = Decimal(budget_raw)
        except Exception:
            budget = Decimal('0')

        job = Job.objects.create(
            client=request.user,
            title=title,
            description=description,
            budget=budget,
            visibility=visibility,
            deadline=deadline if deadline else None
        )
        if project_id:
            proj = Project.objects.filter(pk=project_id, creator=request.user).first()
            if proj:
                job.project = proj
                job.save()

        messages.success(request, "Ish e'loni muvaffaqiyatli yaratildi!")
        return redirect('job_detail', pk=job.pk)

    user_projects = Project.objects.filter(creator=request.user)
    return render(request, 'jobs/create.html', {'user_projects': user_projects})


def job_detail_view(request, pk):
    """Ish tafsilotlari va arizalar"""
    job = get_object_or_404(Job, pk=pk)

    # Xavfsizlik: Private ishlarni faqat client va tanlangan worker ko'ra oladi
    if job.visibility == 'private':
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user != job.client and request.user != job.selected_worker:
            messages.error(request, "Ushbu ish faqat maxsus foydalanuvchi uchun.")
            return redirect('job_list')

    # Auto-approval check for submitted jobs
    job.check_auto_approval()

    proposals = None
    my_proposal = None
    escrow = None

    if request.user.is_authenticated:
        if request.user == job.client:
            proposals = job.proposals.select_related('worker').order_by('-created_at')
            # Escrow ma'lumotini olish (agar mavjud bo'lsa)
            try:
                escrow = job.escrow
            except EscrowPayment.DoesNotExist:
                escrow = None
        else:
            my_proposal = job.proposals.filter(worker=request.user).first()

    deliveries = job.deliveries.select_related('worker').order_by('-created_at')

    return render(request, 'jobs/detail.html', {
        'job': job,
        'proposals': proposals,
        'my_proposal': my_proposal,
        'deliveries': deliveries,
        'escrow': escrow,
    })


# ── PROPOSAL VIEWS ────────────────────────────────────────────────────────────

@login_required
def proposal_create_view(request, pk):
    """Ishga ariza (proposal) topshirish"""
    job = get_object_or_404(Job, pk=pk)

    # Tekshiruvlar
    if job.client == request.user:
        messages.error(request, "O'z ishingizga ariza bera olmaysiz.")
        return redirect('job_detail', pk=pk)

    if job.status != 'open':
        messages.error(request, "Bu ish uchun ariza qabul qilinmayapti.")
        return redirect('job_detail', pk=pk)

    if job.selected_worker:
        messages.error(request, "Bu ish uchun ijrochi allaqachon tanlangan.")
        return redirect('job_detail', pk=pk)

    # Faqat Gold/Platinum foydalanuvchilar worker bo'la oladi
    if not request.user.can_use_pro_features():
        messages.error(request, "Freelancer sifatida ishlamoqchi bo'lsangiz Gold yoki Platinum obuna kerak!")
        return redirect('subscription_plans')

    if request.method == 'POST':
        from decimal import Decimal
        price_raw = request.POST.get('price', '0')
        days = request.POST.get('days', '1')
        message = request.POST.get('message', '').strip()

        if not message:
            messages.error(request, "Xabar yozing.")
            return render(request, 'jobs/proposal_create.html', {'job': job})

        try:
            price = Decimal(price_raw)
        except Exception:
            price = Decimal('0')

        proposal, created = Proposal.objects.get_or_create(
            job=job,
            worker=request.user,
            defaults={
                'price': price,
                'delivery_days': days,
                'message': message
            }
        )

        if not created:
            messages.warning(request, "Siz allaqachon bu ishga ariza bergansiz.")
        else:
            messages.success(request, "Arizangiz muvaffaqiyatli yuborildi!")

        return redirect('job_detail', pk=pk)

    return render(request, 'jobs/proposal_create.html', {'job': job})


@login_required
def proposal_accept_view(request, prop_pk):
    """Ish beruvchi developerni tanlaydi"""
    proposal = get_object_or_404(Proposal, pk=prop_pk, job__client=request.user)
    job = proposal.job

    if job.status != 'open':
        messages.error(request, "Bu ish uchun ijrochi allaqachon tanlangan.")
        return redirect('job_detail', pk=job.pk)

    if job.selected_worker:
        messages.error(request, "Ushbu ish uchun allaqachon ijrochi bor.")
        return redirect('job_detail', pk=job.pk)

    # Boshqa arizalarni rad etish
    job.proposals.exclude(pk=prop_pk).update(status='rejected')

    # Tanlangan arizani tasdiqlash
    proposal.status = 'accepted'
    proposal.save()

    job.selected_worker = proposal.worker
    job.status = 'open'  # To'lov kutilmoqda
    job.save()

    # Escrow yozuvini yaratish (agar mavjud bo'lmasa)
    try:
        escrow = job.escrow  # Allaqachon bor
    except EscrowPayment.DoesNotExist:
        from decimal import Decimal
        amount = proposal.price
        fee = (amount * Decimal('0.06')).quantize(Decimal('0.01'))  # 6% komissiya
        EscrowPayment.objects.create(
            job=job,
            client=job.client,
            worker=proposal.worker,
            amount=amount,
            platform_fee=fee
        )

    try:
        from apps.notifications.service import notify_proposal_accepted
        notify_proposal_accepted(proposal)
    except Exception:
        pass

    # Background email
    try:
        from apps.tasks import send_job_notification_email
        send_job_notification_email.delay(job.pk, 'proposal_accepted')
    except Exception:
        pass

    messages.success(request, f"✅ {proposal.worker.username} tanlandi! Endi to'lovni amalga oshiring.")
    return redirect('job_detail', pk=job.pk)


# ── ESCROW & DELIVERY ─────────────────────────────────────────────────────────

@login_required
def escrow_fund_view(request, pk):
    """To'lovni (escrow) amalga oshirish — balansdan yechish"""
    from decimal import Decimal
    job = get_object_or_404(Job, pk=pk, client=request.user)

    try:
        escrow = job.escrow
    except EscrowPayment.DoesNotExist:
        messages.error(request, "Escrow topilmadi. Avval ijrochi tanlang.")
        return redirect('job_detail', pk=pk)

    if escrow.status == 'funded':
        messages.warning(request, "To'lov allaqachon amalga oshirilgan.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        total = escrow.amount + escrow.platform_fee

        # Balans tekshiruvi
        if request.user.balance < total:
            messages.error(
                request,
                f"Hisobingizda mablag' yetarli emas. "
                f"Kerak: ${total} (ish: ${escrow.amount} + 6% komissiya: ${escrow.platform_fee}). "
                f"Sizda: ${request.user.balance}."
            )
            return render(request, 'jobs/escrow_fund.html', {'job': job, 'escrow': escrow, 'total': total})

        # Mijozdan pul yechish
        request.user.balance -= total
        request.user.save(update_fields=['balance'])

        from apps.accounts.models import Transaction
        Transaction.objects.create(
            user=request.user,
            amount=-total,
            transaction_type='escrow_lock',
            description=f"Escrow uchun muzlatildi: {job.title}"
        )

        escrow.status = 'funded'
        escrow.save()

        job.status = 'funded'
        job.save()

        # Ishchiga bildirishnoma
        try:
            from apps.notifications.service import notify_escrow_funded
            notify_escrow_funded(job)
        except Exception:
            pass

        # Background email
        try:
            from apps.tasks import send_job_notification_email
            send_job_notification_email.delay(job.pk, 'escrow_funded')
        except Exception:
            pass

        messages.success(request, f"💰 ${total} escrow'ga qo'yildi. Ishchi ishni boshlashi mumkin!")
        return redirect('job_detail', pk=job.pk)

    total = escrow.amount + escrow.platform_fee
    return render(request, 'jobs/escrow_fund.html', {'job': job, 'escrow': escrow, 'total': total})


@login_required
def delivery_submit_view(request, pk):
    """Ishchi ishni topshirishi"""
    job = get_object_or_404(Job, pk=pk, selected_worker=request.user)

    # Faqat 'funded' holatda topshirish mumkin
    if job.status not in ['funded', 'in_progress']:
        messages.error(request, "Ishni topshirish uchun avval mijoz to'lov qilishi kerak.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        file = request.FILES.get('file')
        preview = request.FILES.get('preview')
        demo = request.POST.get('demo_link', '').strip()

        if not message:
            messages.error(request, "Xabar yozing.")
            return render(request, 'jobs/delivery_submit.html', {'job': job})

        if not file and not demo:
            messages.error(request, "Fayl yoki demo havola kiritish shart.")
            return render(request, 'jobs/delivery_submit.html', {'job': job})

        Delivery.objects.create(
            job=job,
            worker=request.user,
            message=message,
            file=file,
            preview_image=preview if preview else None,
            demo_link=demo
        )

        job.status = 'submitted'
        job.save()

        # Mijozga bildirishnoma
        try:
            from apps.notifications.service import notify_delivery_submitted
            notify_delivery_submitted(job)
        except Exception:
            pass

        # Background email
        try:
            from apps.tasks import send_job_notification_email
            send_job_notification_email.delay(job.pk, 'delivery_submitted')
        except Exception:
            pass

        messages.success(request, "✅ Ish muvaffaqiyatli topshirildi! Mijoz tasdiqlashini kuting.")
        return redirect('job_detail', pk=job.pk)

    return render(request, 'jobs/delivery_submit.html', {'job': job})


@login_required
def delivery_approve_view(request, pk):
    """Client ishni tasdiqlaydi va pulni workerga chiqaradi"""
    job = get_object_or_404(Job, pk=pk, client=request.user)

    if job.status != 'submitted':
        messages.error(request, "Tasdiqlash uchun ish avval topshirilishi kerak.")
        return redirect('job_detail', pk=pk)

    try:
        escrow = job.escrow
    except EscrowPayment.DoesNotExist:
        messages.error(request, "Escrow topilmadi.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        job.status = 'approved'
        job.save()

        escrow.status = 'released'
        escrow.save()

        # Fayllarni yuklab olishga ruxsat berish
        job.deliveries.all().update(is_downloadable=True)

        # Workerga haqiqiy pul o'tkazish
        worker = job.selected_worker
        if worker:
            worker.balance += escrow.amount
            worker.save(update_fields=['balance'])

            # Log Activity & Award XP (automatically adds 500 XP and handles level up)
            try:
                from apps.accounts.models import UserActivity
                UserActivity.log_activity(worker, 'job_complete')
            except Exception as e:
                print(f"Failed to log job completion activity: {e}")

            from apps.accounts.models import Transaction
            Transaction.objects.create(
                user=worker,
                amount=escrow.amount,
                transaction_type='escrow_release',
                description=f"Ish yakunlandi (Escrow): {job.title}"
            )

        # Bildirishnoma
        try:
            from apps.notifications.service import notify_delivery_approved
            notify_delivery_approved(job)
        except Exception:
            pass

        # Background email
        try:
            from apps.tasks import send_job_notification_email
            send_job_notification_email.delay(job.pk, 'delivery_approved')
        except Exception:
            pass

        messages.success(
            request,
            f"✅ Ish tasdiqlandi! ${escrow.amount} {worker.username if worker else 'ishchi'}ga o'tkazildi."
        )
        return redirect('job_detail', pk=job.pk)

    return redirect('job_detail', pk=pk)


@login_required
def my_jobs_view(request):
    """Foydalanuvchi ishtirok etayotgan barcha ishlar"""
    client_jobs = Job.objects.filter(client=request.user).order_by('-created_at')
    my_proposals = Proposal.objects.filter(worker=request.user).select_related('job', 'job__client').order_by('-created_at')
    working_jobs = Job.objects.filter(selected_worker=request.user).order_by('-created_at')

    return render(request, 'jobs/my_jobs.html', {
        'client_jobs': client_jobs,
        'my_proposals': my_proposals,
        'working_jobs': working_jobs
    })

@login_required
def my_applications_view(request):
    """Foydalanuvchi yuborgan barcha arizalar (proposals)"""
    proposals = Proposal.objects.filter(worker=request.user).select_related(
        'job', 'job__client'
    ).order_by('-created_at')

    return render(request, 'jobs/my_applications.html', {'proposals': proposals})


@login_required
def dispute_open_view(request, pk):
    """Nizo (Dispute) ochish"""
    job = get_object_or_404(Job, pk=pk)
    
    # Faqat client yoki worker nizo ocha oladi
    if request.user != job.client and request.user != job.selected_worker:
        messages.error(request, "Faqat tomonlar nizo ocha oladi.")
        return redirect('job_detail', pk=pk)
        
    if job.status not in ['funded', 'submitted', 'in_progress']:
        messages.error(request, "Bu holatda nizo ochib bo'lmaydi.")
        return redirect('job_detail', pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        if not reason:
            messages.error(request, "Sababini ko'rsating.")
            return render(request, 'jobs/dispute_open.html', {'job': job})
            
        Dispute.objects.create(
            job=job,
            opened_by=request.user,
            reason=reason,
            evidence_files=request.FILES.get('evidence')
        )
        
        job.status = 'disputed'
        job.save()
        
        messages.warning(request, "Nizo ochildi. Admin tez orada ko'rib chiqadi.")
        return redirect('job_detail', pk=pk)
        
    return render(request, 'jobs/dispute_open.html', {'job': job})
