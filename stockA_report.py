import akshare as ak
import smtplib
import ssl
import time
from email.mime.text import MIMEText
from datetime import datetime
import os

# 价位参数永久固定
support_low = 1.40
support_zone_low = 1.41
support_zone_high = 1.43
osc_low = 1.43
osc_high = 1.47
press_1_low = 1.47
press_1_high = 1.49
mid_target = 1.52
neck_low = 1.57
neck_high = 1.59

# 获取TMT指数活跃度（替代板块成交额，境外IP稳定可用）
def get_tmt_hot():
    for _ in range(2):
        try:
            df_idx = ak.index_zh_a_hist(symbol="000998", period="daily",
                                         start_date=datetime.now().strftime("%Y%m%d"),
                                         end_date=datetime.now().strftime("%Y%m%d"))
            amount_wan = float(df_idx.iloc[-1]["成交额"])
            # 成交额（万元）转为亿元
            amount_yi = amount_wan / 10000

            # 直接分档位，不再计算百分比，杜绝大数错误
            if amount_yi >= 2000:
                return 46
            elif amount_yi >= 1600:
                return 42
            elif amount_yi >= 1200:
                return 36
            else:
                return 30
        except Exception:
            time.sleep(1)
    # 异常中性值
    return 36

# 获取515080收盘价（原有稳定接口不变）
def get_etf_price():
    today = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.fund_etf_hist_em(symbol="515080", start_date=today, end_date=today)
        return round(float(df.iloc[-1]["收盘"]), 3)
    except Exception:
        return 0

# 策略判断（保留全部突破规则+颈线止盈）
def build_report(ratio, price):
    if ratio >= 45:
        crowd = "极度抱团｜止盈科技，盈利加仓红利"
    elif ratio >= 40:
        crowd = "热度升温｜继续持有科技仓位"
    elif ratio >= 33:
        crowd = "热度降温｜等待科技回调低吸"
    else:
        crowd = "资金流出成长赛道，红利板块占优"

    if price <= support_low:
        price_text = "已经跌破强支撑1.40，可分批打底仓，严控总仓位"
    elif support_zone_low <= price <= support_zone_high:
        price_text = "靠近支撑区间1.41-1.43，逢低分批布局买入"
    elif osc_low < price < osc_high:
        price_text = "箱体中段震荡，保持持仓不动，避免频繁做T"
    elif press_1_low <= price <= press_1_high:
        price_text = "抵达第一短期压力1.47-1.49，分批减仓止盈，不追高；仅单日冲高不算有效突破"
    elif press_1_high < price < mid_target:
        price_text = "突破确认规则：连续两个交易日日线收盘价站稳1.49，并且盘中不再跌破1.47，才算有效突破；无量单日冲高回落属于假突破。突破成立则持有上看1.52；一旦收盘跌回1.47下方，突破失效，重新回到箱体震荡思路"
    elif mid_target <= price < neck_low:
        price_text = "到达中继压力1.52，先行减掉部分底仓，保留少量仓位试探上方颈线压力"
    elif neck_low <= price <= neck_high:
        price_text = "进入日线历史颈线区间1.57~1.59，此处为前期高点成交密集区，逐步全线清仓止盈"
    else:
        price_text = "行情震荡观望"

    content = f"""
=====【收盘交易日报】{datetime.now().strftime("%Y-%m-%d")}
TMT赛道热度值：{ratio}%
资金状态：{crowd}
中证红利515080现价：{price}
操作指令：{price_text}
"""
    return content

# 邮件发送函数不变
def send_email(content):
    try:
        sender = os.environ.get("MAIL_SENDER")
        receiver = os.environ.get("MAIL_RECEIVER")
        auth_code = os.environ.get("MAIL_AUTH")
        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "每日收盘盯盘日报"
        msg["From"] = sender
        msg["To"] = receiver
        context = ssl._create_unverified_context()
        server = smtplib.SMTP_SSL("smtp.qq.com", 465, context=context, timeout=15)
        server.login(sender, auth_code)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"邮件异常：{e}")

if __name__ == "__main__":
    ratio_data = get_tmt_hot()
    price_data = get_etf_price()
    mail_text = build_report(ratio_data, price_data)
    print(mail_text)
    send_email(mail_text)
    # 临时刷新cron缓存
