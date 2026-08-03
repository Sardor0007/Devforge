from django.shortcuts import redirect
from django.contrib import messages

class SubscriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Foydalanuvchi login qilganligini tekshirish
        user = getattr(request, 'user', None)
        authenticated = user.is_authenticated if user else False

        # PRO funksiyalar uchun ruxsat tekshiruvi
        if authenticated and hasattr(user, 'can_use_pro_features'):
            if not user.can_use_pro_features():
                path = request.path

                # Faqat PRO obunachilar kiradigan manzillar
                blocked_prefixes = [
                    '/studio/',
                    '/workspace/',
                    '/learn/create-course/',
                    '/marketplace/create/',
                    '/assets/upload/',
                ]

                for prefix in blocked_prefixes:
                    if path.startswith(prefix):
                        messages.warning(
                            request,
                            "⚠️ Ushbu bo'limdan foydalanish uchun Pro yoki Studio obunasi kerak!"
                        )
                        return redirect('subscription_plans')

        return self.get_response(request)
