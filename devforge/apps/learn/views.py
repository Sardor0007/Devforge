from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from .models import Course, Lesson, Category, Enrollment, LessonProgress, Comment
from .forms import CourseForm, LessonForm

def course_list(request):
    # Auto-populate categories if empty
    # if not Category.objects.exists():
    #     ... (this should be a management command)

    courses = Course.objects.all().order_by('-created_at')
    
    # Search logic
    query = request.GET.get('q')
    if query:
        courses = courses.filter(title__icontains=query) | courses.filter(description__icontains=query)

    categories = Category.objects.all()
    return render(request, 'learn/course_list.html', {
        'courses': courses,
        'categories': categories
    })

@login_required
def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    lessons = course.lessons.all()
    is_enrolled = Enrollment.objects.filter(user=request.user, course=course).exists()
    
    return render(request, 'learn/course_detail.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled
    })

@login_required
def enroll_course(request, slug):
    """Kursga yozilish — bepul yoki balansdan to'lab"""
    from decimal import Decimal
    course = get_object_or_404(Course, slug=slug)

    # Allaqachon yozilganmi?
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return redirect('course_detail', slug=slug)

    # Muallif o'z kursiga bepul kiradi
    if course.author == request.user:
        Enrollment.objects.get_or_create(user=request.user, course=course)
        first_lesson = course.lessons.first()
        if first_lesson:
            return redirect('lesson_detail', course_slug=slug, lesson_id=first_lesson.id)
        return redirect('course_detail', slug=slug)

    # Pullik kurs bo'lsa balansni tekshiramiz
    if not course.is_free:
        if request.user.balance < course.price:
            messages.error(
                request,
                f"Hisobingizda mablag' yetarli emas. Kurs narxi: ${course.price}. "
                f"Sizda: ${request.user.balance}."
            )
            return redirect('subscription_plans')

        # Balansdan yechish va muallifga o'tkazish
        request.user.balance -= course.price
        request.user.save(update_fields=['balance'])

        author = course.author
        author.balance += course.price
        author.save(update_fields=['balance'])

        Enrollment.objects.create(user=request.user, course=course, price_paid=course.price)
        messages.success(request, f"'{course.title}' kursiga muvaffaqiyatli yozildingiz! ${course.price} yechildi.")
    else:
        Enrollment.objects.get_or_create(user=request.user, course=course)
        messages.success(request, f"'{course.title}' kursiga yozildingiz!")

    return redirect('course_detail', slug=slug)

@login_required
def lesson_detail(request, course_slug, lesson_id):

    course = get_object_or_404(Course, slug=course_slug)
    lesson = get_object_or_404(Lesson, id=lesson_id, course=course)

    # Enrollment tekshiruvi
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        return redirect('course_detail', slug=course_slug)

    # Dars ko'rilgan deb belgilash (avtomatik)
    progress, _ = LessonProgress.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    if not progress.completed:
        from django.utils import timezone as tz
        progress.completed = True
        progress.completed_at = tz.now()
        progress.save(update_fields=['completed', 'completed_at'])

    # Keyingi va oldingi darslar
    next_lesson = course.lessons.filter(order__gt=lesson.order).first()
    prev_lesson = course.lessons.filter(order__lt=lesson.order).last()

    return render(request, 'learn/lesson_detail.html', {
        'course': course,
        'lesson': lesson,
        'lessons': course.lessons.all(),
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
        'comments': lesson.comments.all().order_by('-created_at'),
        'progress_percent': enrollment.progress_percent,
    })

@login_required
def add_comment(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        if text:
            from .models import Comment
            Comment.objects.create(lesson=lesson, user=request.user, text=text)
    return redirect('lesson_detail', course_slug=lesson.course.slug, lesson_id=lesson.id)
@login_required
def my_courses(request):
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    return render(request, 'learn/my_courses.html', {
        'enrollments': enrollments
    })

@login_required
def create_course(request):
    # Limit tekshiruvi
    from django.utils import timezone
    from datetime import timedelta
    last_month = timezone.now() - timedelta(days=30)
    created_count = Course.objects.filter(author=request.user, created_at__gte=last_month).count()
    limit = request.user.get_upload_limit()

    if created_count >= limit:
        messages.error(request, f"Sizning oylik yuklash limitingiz ({limit} ta) tugagan. Platinum obunaga o'ting yoki kutib turing.")
        return redirect('subscription_plans')

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.author = request.user
            course.slug = slugify(course.title)
            course.save()
            return redirect('add_lesson', slug=course.slug)
    else:
        form = CourseForm()
    return render(request, 'learn/create_course.html', {'form': form})

@login_required
def add_lesson(request, slug):
    course = get_object_or_404(Course, slug=slug, author=request.user)
    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            if 'add_another' in request.POST:
                return redirect('add_lesson', slug=course.slug)
            return redirect('course_detail', slug=course.slug)
    else:
        form = LessonForm()
    return render(request, 'learn/add_lesson.html', {'form': form, 'course': course})
