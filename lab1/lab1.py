import pandas as pd
import matplotlib.pyplot as plt

path = "GOOGL_stock_data.csv"
df_raw = pd.read_csv(path)

# 1.1
print("Raw shape:", df_raw.shape)
print(df_raw.head(5))

# 1.2
keep_cols = [
    "Date", "Open", "High", "Low", "Close", "Volume",
    "Daily_Return_Pct", "Year", "Month", "Day_of_Week"
]
df = df_raw[keep_cols].copy()

# 1.3
df = df.dropna(subset=["Date"])

# 1.4
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])
df["is_positive_return"] = df["Daily_Return_Pct"] > 0

# 2.1
print("Rows after cleaning:", len(df))

# 2.2
close_threshold = df["Close"].quantile(0.90)
df_close_hi = df[df["Close"] > close_threshold].copy()

print("Close p90:", close_threshold)
print("Count Close > p90:", len(df_close_hi))
print("Avg Volume (filtered):", df_close_hi["Volume"].mean())

print(df_close_hi.nlargest(10, "Close")[["Date", "Close"]])

# 2.3
cond1 = df["Day_of_Week"].eq("Monday")
date_str = df["Date"].dt.strftime("%Y-%m-%d")
cond2 = date_str.str.contains("-01-")

print("Count Monday:", int(cond1.sum()))
print("Count January:", int(cond2.sum()))
print("Count (1 AND 2):", int((cond1 & cond2).sum()))

cnt_1_not_2 = int((cond1 & ~cond2).sum())
print("Share (1 AND NOT 2):", cnt_1_not_2 / len(df))
print("Count (NOT 1 AND NOT 2):", int((~cond1 & ~cond2).sum()))

# 2.4
cnt_month_1 = int((df["Month"] == 1).sum())
v_lo, v_hi = df["Volume"].quantile(0.10), df["Volume"].quantile(0.20)
cnt_volume_range = int(((df["Volume"] >= v_lo) & (df["Volume"] <= v_hi)).sum())

print("Count Month==1:", cnt_month_1)
print("Count Volume in [p10, p20]:", cnt_volume_range)
print("Month==1 > VolumeRange?:", cnt_month_1 > cnt_volume_range)

# 2.5
vol_threshold = df["Volume"].quantile(0.95)
df_sig = df[df["Volume"] > vol_threshold].copy()

print("Volume p95:", vol_threshold)
print("Significant count:", len(df_sig))
print(df_sig.nlargest(5, "Close")[["Date", "Close", "Volume", "Day_of_Week"]])

top10_by_high = df_sig.sort_values("High", ascending=False).head(10)
print("Median Daily_Return_Pct for top10 by High:", top10_by_high["Daily_Return_Pct"].median())

# 2.6
compare_df = pd.DataFrame({
    "category_name": ["2020", "2021"],
    "total_records": [len(df[df["Year"] == 2020]), len(df[df["Year"] == 2021])],
    "average_value": [df[df["Year"] == 2020]["Close"].mean(), df[df["Year"] == 2021]["Close"].mean()],
})
print(compare_df)

# 2.7.1
close_95 = df["Close"].quantile(0.95)
complex_mask = (
    ((df["Year"] >= 2020) & (df["is_positive_return"])) |
    (df["Close"] > close_95)
) & ~(df["Day_of_Week"].eq("Friday"))

df_complex = df[complex_mask].copy()
print("Complex filter count:", len(df_complex))
print(df_complex.head(10))

# 2.7.2
df_plot = df.sort_values("Date").set_index("Date")
df_plot["Close_MA30"] = df_plot["Close"].rolling(30).mean()

ax = df_plot[["Close", "Close_MA30"]].plot(title="GOOGL Close та 30-day Moving Average")
ax.set_xlabel("Date")
ax.set_ylabel("Price")
plt.show()
