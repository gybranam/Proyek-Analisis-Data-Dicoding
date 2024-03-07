import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')



def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_purchase_timestamp").agg(
        {"order_id": "nunique", "order_item_value": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "order_item_value": "revenue"}, inplace=True
    )

    return daily_orders_df

def create_category_sum_order_df(df):
    category_sum_order_df = (
        df.groupby("product_category_name_english_x")
        .order_id.nunique()
        .sort_values(ascending=False)
        .reset_index()
    )
    category_sum_order_df.columns = ["category", "order_count"]
    return category_sum_order_df


def create_category_revenue_df(df):
    category_revenue_df = (
        df.groupby("product_category_name_english_x")
        .order_item_value.sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    category_revenue_df.columns = ["category", "revenue"]
    return category_revenue_df

def create_bystate_df(df):
    bystate_df = (
        df.groupby(by="customer_state").customer_unique_id.nunique().reset_index()
    )
    bystate_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    return bystate_df


def create_bycity_df(df):
    bycity_df = (
        df.groupby(by="customer_city").customer_unique_id.nunique().reset_index()
    )
    bycity_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    return bycity_df




all_df = pd.read_csv("main_data.csv")

datetime_columns = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
   
    st.image("img/logo.jpeg")

    
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    
    end_date += pd.DateOffset(days=1)

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date))
    & (all_df["order_purchase_timestamp"] <= str(end_date))
]


daily_orders_df = create_daily_orders_df(main_df)
category_sum_order_df = create_category_sum_order_df(main_df)
category_revenue_df = create_category_revenue_df(main_df)
bystate_df = create_bystate_df(main_df)
bycity_df = create_bycity_df(main_df)


st.header("E-Commerce Dashboard :")

st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "BRL", locale="pt_BR"
    )
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(20, 8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=1.5,
    color="teal",
)
ax.tick_params(axis="y", labelsize=20)
ax.tick_params(axis="x", labelsize=20)

st.pyplot(fig)

st.subheader("Highest and Lowest Performing Product Category by Number of Order")


fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2, 1]})

colors = ["blue", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]


sns.barplot(
    x="order_count",
    y="category",
    data=category_sum_order_df.head(5),
    palette=colors,
    ax=axes[0],
)
axes[0].set_ylabel(None)
axes[0].set_xlabel(None)
axes[0].set_title("Highest Performing Product Category", loc="center", fontsize=16)
axes[0].tick_params(axis="x", labelsize=14)
axes[0].tick_params(axis="y", labelsize=14)

axes[1].set_ylabel(None)
axes[1].set_xlabel(None)
axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].set_title("Lowest Performing Product Category", loc="center", fontsize=16)
axes[1].tick_params(axis="x", labelsize=14)
axes[1].tick_params(axis="y", labelsize=14)

st.pyplot(fig)




# Hitung 10 kota dengan total pendapatan tertinggi
top_cities_by_revenue = main_df.groupby("customer_city")["payment_value"].sum().reset_index().sort_values("payment_value", ascending=False).head(10)

# Visualisasi 10 kota dengan total pendapatan tertinggi
st.subheader("Cities Generating the Highest Revenue")

# Membuat figure dan axes untuk matplotlib
fig, ax = plt.subplots(figsize=(10, 6))

# Membuat barplot
sns.barplot(x="payment_value", y="customer_city", data=top_cities_by_revenue, palette='plasma', ax=ax)
ax.set_xlabel("Total Revenue")
ax.set_ylabel("Cities")
ax.set_title("Top 10 Cities by Revenue")

# Tampilkan plot di Streamlit
st.pyplot(fig)


st.subheader("Highest and Lowest Performing Product Category by Revenue (R$)")

# Membuat figure dengan 2 subplot
fig, axes = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2, 1]})

colors = ["blue", "lightgrey", "lightgrey", "lightgrey", "lightgrey"]

# Plot untuk best product category by revenue
sns.barplot(
    x="revenue",
    y="category",
    data=category_revenue_df.head(5),
    palette=colors,
    ax=axes[0],
)
axes[0].set_ylabel(None)
axes[0].set_xlabel(None)
axes[0].set_title("Highest Revenue Categories", loc="center", fontsize=16)
axes[0].tick_params(axis="x", labelsize=14)
axes[0].tick_params(axis="y", labelsize=14)

# Plot untuk worst product category
sns.barplot(
    x="revenue",
    y="category",
    data=category_revenue_df.sort_values(by="revenue", ascending=True).head(5),
    palette=colors,
    ax=axes[1],
)
axes[1].set_ylabel(None)
axes[1].set_xlabel(None)
axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].set_title("Lowest Revenue Categories", loc="center", fontsize=16)
axes[1].tick_params(axis="x", labelsize=14)
axes[1].tick_params(axis="y", labelsize=14)

st.pyplot(fig)



st.caption("Copyright (c) Gybran Khairul Anam 2024")