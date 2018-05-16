from django import template

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