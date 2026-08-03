from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def gamelab_view(request):
    """
    GameLab — O'yinlarni test qilish va feedback olish bo'limi.
    Hali ishlab chiqish jarayonida.
    """
    return render(request, 'gamelab/index.html')

@login_required
def publisher_hub_view(request):
    """
    Publisher Hub — Nashriyotchilar bilan bog'lanish bo'limi.
    Hali ishlab chiqish jarayonida.
    """
    return render(request, 'publisher/index.html')
