import akshare as ak
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

# 交易参数保持不变
support_low = 1.40
support_area = [1.41, 1.43]
pressure_area = [1.47, 1.49]
neckline = 1.54

# 抓取TMT四个板块成交额
def get_tmt_ratio():
    try:
        trade_sum = 0
        df_dz = ak.stock_board_industry_summary_ths(symbol="电子元件")
        trade_sum += float(df_dz.iloc[0]["成交额"])
        df_jsj = ak.stock_board_industry_summary_ths(symbol="计算机应用")
        trade_sum += float(df_jsj.iloc[0]["成交额"])
        df_tx = ak.stock_board_industry_summary_ths(symbol="通信设备")
        trade_sum += float(df_tx.iloc[0]["成交额"])
        df_cm = ak.stock_board_industry_summary_ths(symbol="文化传媒")
        trade_sum += float(df_cm.iloc[0]["成交额"])

        df_market = ak.stock_market_fund_flow()
        total_market = float(df_market.iloc[0]["成交额"])
        ratio = round(trade_sum / total_market * 100, 2)
        return ratio
    except Exception:
        return -999

# 获取ETF收盘价
def get_etf_price():
    today = datetime.now().strftime("%Y%m%d")
    try:
        df = ak.fund_etf_hist_em(symbol="515080", start_date=today, end_date=today)
        return round(float(df.iloc[-1]["收盘"]), 3)
    except Exception:
        return 0

# 生成日报文本
def build_report(ratio, price):
    if ratio < 0:
        crowd = "数据抓取失败"
    elif ratio >= 45:
        crowd = "极度抱团｜止盈科技，盈利加仓红利"
    elif ratio >= 40:
        crowd = "热度升温｜继续持有科技仓位"
    elif ratio >= 33:
        crowd = "热度降温｜等待科技回调低吸"
    else:
        crowd = "资金回流防御板块"

    if price <= 0:
        price_text = "价格获取失败"
    elif price <= support_low:
        price_text = "极限低点1.40，大额加仓窗口"
    elif support_area[0] <= price <= support_area[1]:
        price_text = "支撑区1.41~1.43，科技盈利转入加仓"
    elif pressure_area[0] <= price <= pressure_area[1]:
        price_text = "压力区1.47~1.49，执行反T卖出机动仓"
    elif price >= neckline:
        price_text = "站稳颈线1.54，取消频繁做T"
    else:
        price_text = "箱体中段震荡，明日无需盯盘"

    text = f"""
=====【收盘交易日报】{datetime.now().strftime("%Y-%m-%d")}
TMT科技板块成交占比：{ratio}%
资金状态：{crowd}
中证红利515080现价：{price}
操作指令：{price_text}
"""
    return text

# 发送QQ邮箱（新增邮件发送函数）
def send_email(content):
    # 从GitHub密钥读取账号密码，明文不写在代码里
    sender = os.environ.get("MAIL_SENDER")
    receiver = os.environ.get("MAIL_RECEIVER")
    auth_code = os.environ.get("MAIL_AUTH")

    msg = MIMEText(content, "plain", "utf-8")
    msg["Subject"] = "每日收盘盯盘日报"
    msg["From"] = sender
    msg["To"] = receiver

    # QQ邮箱SMTP服务器
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(sender, auth_code)
    server.sendmail(sender, receiver, msg.as_string())
    server.quit()

if __name__ == "__main__":
    ratio = get_tmt_ratio()
    price = get_etf_price()
    msg_text = build_report(ratio, price)
    print(msg_text)
    send_email(msg_text)
