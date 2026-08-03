import os
import json
import requests
from celery import shared_task
from django.core.cache import cache

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
ANTHROPIC_URL     = 'https://api.anthropic.com/v1/messages'
MODEL             = 'claude-sonnet-4-20250514'

@shared_task
def call_claude_async(system_prompt, user_prompt, max_tokens=1000):
    """Anthropic API ga so'rov yuborish (Async)"""
    if not ANTHROPIC_API_KEY:
        return {'error': 'AI_KEY_MISSING'}

    try:
        resp = requests.post(
            ANTHROPIC_URL,
            headers={
                'x-api-key': ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json',
            },
            json={
                'model': MODEL,
                'max_tokens': max_tokens,
                'system': system_prompt,
                'messages': [{'role': 'user', 'content': user_prompt}],
            },
            timeout=30,
        )
        data = resp.json()
        if resp.status_code == 200:
            return {'result': data['content'][0]['text']}
        return {'error': data.get('error', {}).get('message', 'API xatosi')}
    except Exception as e:
        return {'error': str(e)}
