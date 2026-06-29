import akshare as ak
from datetime import datetime

support_low = 1.40
support_area = [1.41, 1.43]
pressure_area = [1.47, 1.49]
neckline = 1.54

def get_tmt_ratio():
    df_flow = ak.stock_sector_fund_flow_summary()
    total_tmt = 0
    for industry in ["电子", "计算机", "通信", "传媒"]:
        row = df_flow[df_flow["行业"] == industry]
        if not row.empty:
            total_tmt += float(row.iloc[0]["成交额-亿"])

    df_market = ak.stock_market_fund_flow()
    sh = float(df_market[df_market["市场"]=="沪市"].iloc[0]["成交额-亿"])
    sz = float(df_market[df_market["市场"]=="深市"].iloc[0]["成交额-亿"])
    total_market = sh + sz
    ratio = round((total_tmt / total_market)*100, 2)
    return ratio

def get_etf_price():
    today = datetime.now().strftime("%Y%m%d")
    df = ak.fund_etf_hist_em(symbol="515080", start_date=today, end_date=today)
    return round(float(df.iloc[-1]["收盘"]), 3)

def build_report(ratio, price):
    if ratio >= 45:
        crowd = "极度抱团｜止盈科技，盈利加仓红利"
    elif ratio >= 40:
        crowd = "热度升温｜继续持有科技仓位"
    elif ratio >= 33:
        crowd = "热度降温｜等待科技回调低吸"
    else:
        crowd = "资金回流防御板块"

    if price <= support_low:
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

if __name__ == "__main__":
    ratio = get_tmt_ratio()
    price = get_etf_price()
    print(build_report(ratio, price))
