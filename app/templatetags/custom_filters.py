from django import template
from django.utils import timezone
from django.utils import dateformat
from datetime import datetime,timedelta

register = template.Library()

@register.filter
def contain_fin(querydict):
    # ややこしいが、「完了済含む」押したときには実際の状態の逆が入る
    # ⇒次にボタン押したときに期待される状態が入る
    contain_fin = querydict.get('contain_fin')
    if contain_fin == "0/" or contain_fin is None:
        contain_fin = "1"
    else:
        contain_fin = "0"
    return contain_fin

@register.filter
def log_date(querydict):
    # 日付ごとのログ抽出時の対象日付
    log_date = querydict.get('log_date')
    if log_date is None or log_date=="/":
        log_date = dateformat.format(datetime.now(), 'Y-m-d')
    return log_date

@register.filter
def log_from(querydict):
    # 日付ごとのログ抽出時の対象日付
    log_from = querydict.get('log_from')
    if log_from is None or log_from=="/":
        # 今日含め一週間分のログを取得
        log_from = dateformat.format(datetime.now()+timedelta(days=-6), 'Y-m-d')
    return log_from

@register.filter
def log_to(querydict):
    # 日付ごとのログ抽出時の対象日付
    log_to = querydict.get('log_to')
    if log_to is None or log_to=="/":
        log_to = dateformat.format(datetime.now(), 'Y-m-d')
    return log_to
