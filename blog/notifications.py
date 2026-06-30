# coding=utf-8
from __future__ import unicode_literals

import logging
import threading

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.db import close_old_connections

from MyBlog.env import env, env_bool, env_list
from .seo import absolute_url


logger = logging.getLogger('django')


def lead_subject(lead):
    return 'Mongona 新合作需求：%s / %s' % (lead.name, lead.get_demand_type_display())


def lead_body(lead):
    admin_url = absolute_url('/admin/blog/sponsorlead/%s/change/' % lead.pk)
    rows = (
        ('线索 ID', lead.pk),
        ('称呼', lead.name),
        ('公司/产品', lead.company or '-'),
        ('联系方式', lead.contact),
        ('需求类型', lead.get_demand_type_display()),
        ('预算', lead.get_budget_display()),
        ('来源页面', lead.source_path or '-'),
        ('访问 IP', lead.ip or '-'),
        ('来路', lead.referer or '-'),
        ('后台查看', admin_url),
        ('需求描述', lead.message or '-'),
    )
    return '\n'.join(['%s：%s' % (name, value) for name, value in rows])


def markdown_body(lead):
    return lead_body(lead).replace('\n', '\n\n')


def email_recipients():
    recipients = env_list('SPONSOR_LEAD_NOTIFY_EMAILS')
    if recipients:
        return recipients
    return env_list('ADMIN_EMAILS')


def send_lead_email(lead, subject, body):
    if not env_bool('SPONSOR_LEAD_EMAIL_ENABLED', True):
        return
    recipients = email_recipients()
    if not recipients:
        return
    if not getattr(settings, 'EMAIL_HOST', ''):
        logger.warning('Sponsor lead email skipped: EMAIL_HOST is empty.')
        return
    from_email = (
        env('SPONSOR_LEAD_FROM_EMAIL')
        or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        or getattr(settings, 'EMAIL_HOST_USER', '')
    )
    if not from_email:
        logger.warning('Sponsor lead email skipped: from email is empty.')
        return
    send_mail(subject, body, from_email, recipients, fail_silently=False)


def webhook_payload(kind, lead, subject, body):
    content = markdown_body(lead)
    if kind in ('wechat_work', 'wecom', 'qiye_wechat'):
        return {'msgtype': 'markdown', 'markdown': {'content': '**%s**\n\n%s' % (subject, content)}}
    if kind in ('dingtalk', 'dingding'):
        return {'msgtype': 'markdown', 'markdown': {'title': subject, 'text': '### %s\n\n%s' % (subject, content)}}
    if kind in ('serverchan', 'server_chan', 'server酱'):
        return {'title': subject, 'desp': body}
    if kind == 'pushplus':
        payload = {'title': subject, 'content': content, 'template': 'markdown'}
        token = env('SPONSOR_LEAD_WEBHOOK_TOKEN', '')
        if token:
            payload['token'] = token
        return payload
    if kind == 'bark':
        return {'title': subject, 'body': body, 'level': 'active'}
    return {
        'title': subject,
        'content': body,
        'lead_id': lead.pk,
        'source': lead.source_path,
        'contact': lead.contact,
    }


def send_lead_webhook(lead, subject, body):
    if not env_bool('SPONSOR_LEAD_WEBHOOK_ENABLED', True):
        return
    url = env('SPONSOR_LEAD_WEBHOOK_URL', '').strip()
    if not url:
        return
    kind = env('SPONSOR_LEAD_WEBHOOK_KIND', 'generic').strip().lower()
    timeout = float(env('SPONSOR_LEAD_NOTIFY_TIMEOUT_SECONDS', '4') or 4)
    response = requests.post(url, json=webhook_payload(kind, lead, subject, body), timeout=timeout)
    if response.status_code >= 400:
        logger.warning('Sponsor lead webhook failed: status=%s body=%s', response.status_code, response.text[:300])


def send_sponsor_lead_notification(lead):
    subject = lead_subject(lead)
    body = lead_body(lead)
    try:
        send_lead_email(lead, subject, body)
    except Exception as exc:
        logger.warning('Sponsor lead email notification failed: %s', exc)
    try:
        send_lead_webhook(lead, subject, body)
    except Exception as exc:
        logger.warning('Sponsor lead webhook notification failed: %s', exc)


def notify_sponsor_lead_async(lead_id):
    from blog.models import SponsorLead

    def runner():
        close_old_connections()
        try:
            lead = SponsorLead.objects.get(pk=lead_id)
        except Exception as exc:
            logger.warning('Sponsor lead notification skipped: %s', exc)
            return
        try:
            send_sponsor_lead_notification(lead)
        finally:
            close_old_connections()

    thread = threading.Thread(target=runner, name='sponsor-lead-notify-%s' % lead_id)
    thread.daemon = True
    thread.start()
