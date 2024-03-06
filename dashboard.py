import streamlit as st

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

# Dashboard Functions
def create_daily_order_df(df):
    daily_order_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',
        'payment_value': 'sum'
    })

    daily_order_df = daily_order_df.reset_index()

    daily_order_df = daily_order_df.rename(columns={
        'order_id': 'order_count',
        'payment_value': 'total_sales'
    })

    return daily_order_df

def create_sum_order(df):
    sum_order = df.groupby('product_category_name_english').quantity_x.sum().sort_values(ascending=False).reset_index()
    return sum_order

def create_bystate(df):
    bystate_df = df.groupby('customer_state').customer_id.nunique().reset_index()

    bystate_df.rename(columns={
        'customer_id': 'customer_count'
    }, inplace=True)

    return bystate_df

def create_by_review(df):
    review_customer = df.groupby(by="review_score").agg({
        "customer_id": "nunique",
        "payment_value": "sum",
        "customer_city": pd.Series.mode
    })

    review_customer = review_customer.rename(columns={
        'customer_id': 'customer_count',
        'payment_value': 'total_sales',
        'customer_city': 'most_popular_city'
    })

    return review_customer

def create_by_photoqty(df):
    photos_qty_analysis = df.groupby(by="product_photos_qty").agg({
        "product_id": "nunique",
        "seller_city": pd.Series.mode,
        "price": "sum",
        "product_category_name_english": pd.Series.mode
    })

    photos_qty_analysis = photos_qty_analysis.rename(columns={
        'product_id': 'product_count',
        'seller_city': 'most_popular_city',
        'price': 'total_sales',
        'product_category_name_english': 'most_popular_category'
    })

    return photos_qty_analysis

def create_by_paymenttype(df):
    order_payment_df = df.groupby(by='payment_type').agg({
        "order_id": "nunique",
        "payment_value": "mean"
    })

    order_payment_df = order_payment_df.rename(columns={
        'order_id': 'order_count',
        'payment_value': 'average_value'
    })

    return order_payment_df

def create_bycity(df):
    top_cities = df.groupby(by="customer_city").agg({
        'customer_id': "nunique"
    }).reset_index()

    top_cities = top_cities.rename(columns={
        'customer_id': 'count'
    })

    top_cities = top_cities.sort_values(by='count', ascending=False).head(10)

    return top_cities

def create_bycategory(df):
    top_product = df.groupby(by="product_category_name_english").agg({
        'order_id': 'nunique',
        'seller_city': pd.Series.mode
    }).reset_index()

    top_product = top_product.rename(columns={
        'order_id': 'total_sales',
        'seller_city': 'sold_by'
    })

    top_product = top_product.sort_values(by='total_sales', ascending=False).head(10)

    return top_product

# Read Data
all_product_df = pd.read_csv('all_product.csv')
all_order_df = pd.read_csv('all_order.csv')

# handling date times
datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']

for column in datetime_columns:
    all_order_df[column] = pd.to_datetime(all_order_df[column])

# Dashboard Frontend
with st.sidebar:
    st.title("Menu")

    home_button = st.button("Home")
    data_intro_button = st.button("Data Introduction")
    eda_button = st.button("Exploratory Data Analysis")
    explain_button = st.button("Explanatory Data Analysis")

if home_button:
    st.title("Welcome to Shayna's Dashboard")
    st.markdown("This project is designed to meet the final requirement of the Dicoding course 'Learning Data Analysis with Python'")

if data_intro_button:
    st.title("Data Introduction")
    st.header("E-Commerce Public Dataset")

    st.markdown("""
        This dataset illustrates the overall sales trends in Brazil, encompassing information about the products, incoming orders, product sellers, as well as additional details such as location, zip code, and the English names of product categories. In this data analysis, the dataset will be utilized to explore trends in the sales of various types of products in Brazil. 
                
        **Business question addressed in this analysis include:**
        1. Identifying the city that corresponds to the highest volume of orders for each review score.
        2. How can the platform enhance the presentation of products, especially in categories with fewer photos, to improve the overall shopping experience and potentially boost sales? 
                
        However, it's important to note that the analysis is not confined solely to these questions; it extends beyond to capture additional insights from the dataset.
    """)

    st.subheader("Dataset Information")
    st.markdown("""
        The dataset consists of 9 different data;
        * Customers Dataset
        * Orders Dataset
        * Order Items Dataset
        * Order Payment Dataset
        * Order Reviews Dataset
        * Geolocation Dataset
        * Products Dataset
        * Product Category Dataset
        * Sellers Dataset
    """)

if eda_button:
    st.title("Exploratory Data Analysis")

    tab_titles = ['Overall Exploration', 'Statistics']
    tab1, tab2 = st.tabs(tab_titles)

    with tab1:
        col1, col2 = st.columns(2)
        total_order = create_daily_order_df(all_order_df)

        with col1:
            total = total_order.order_count.sum()
            st.metric("Total Orders", value=total)

        with col2:
            sales = format_currency(total_order.total_sales.sum(), "BRL", locale='es_CO')
            st.metric("Total Sales", value=sales)

        st.subheader("Overall Order Dataset Histogram")
        order_hist = all_order_df.select_dtypes(include=['number']).columns
        
        col1, col2 = st.columns(2)

        for column in order_hist[len(order_hist)//2:]:
            fig, ax = plt.subplots()
            ax.hist(all_order_df[column], bins=30, color="skyblue", edgecolor="black", linewidth=1.0)
            ax.set_xlabel("Values")
            ax.set_ylabel("Frequency")
            ax.set_title(f'{column}')
            col1.pyplot(fig)

        for column in order_hist[:len(order_hist)//2]:
            fig, ax = plt.subplots()
            ax.hist(all_order_df[column], bins=30, color="skyblue", edgecolor="black", linewidth=1.0)
            ax.set_xlabel("Values")
            ax.set_ylabel("Frequency")
            ax.set_title(f'{column}')
            col2.pyplot(fig)

    with tab2:
        bycity = create_bycity(all_order_df).head(10)

        fig, ax = plt.subplots(figsize=(60, 20))
        sns.barplot(
            y = 'count',
            x = 'customer_city',
            data = bycity,
            ax = ax
        )

        st.header("Customer Statistic")

        most_popular = bycity.customer_city.iloc[0]
        st.metric("Most Popular City", value=most_popular)

        ax.set_title("Top 10 Customer's City", loc="center", fontsize=50)
        ax.set_ylabel('Customer Count')
        ax.set_xlabel('City')
        ax.tick_params(axis='x', labelsize=35)
        ax.tick_params(axis='y', labelsize=30)
        st.pyplot(fig)

        st.markdown("""\n
            **Exploration**
                    
            In the data exploration, it is checked where most customers in Brazil come from. It turns out that São Paulo has the most customers, with 15,540 people. This means a lot of people in São Paulo use online shopping. Rio de Janeiro and Belo Horizonte also have many customers, but São Paulo is the top city.
            \n
            São Paulo might have more customers because it's a big city with lots of jobs and opportunities. People living there might shop online more. Knowing where our customers are helps us plan better for things like advertising and delivering products. Since São Paulo has the most customers, it's important to focus on that city for our business.
        """)

        st.header('Products Statistic')
        product_sales = create_bycategory(all_product_df).head(10)
        best_product = product_sales.product_category_name_english.iloc[0]
        st.metric("Most Popular Product", value=best_product)

        fig, ax = plt.subplots(figsize=(70, 20))
        sns.barplot(
            y = 'total_sales',
            x = 'product_category_name_english',
            data = product_sales,
            ax = ax
        )

        ax.set_title('Top 10 Products Ordered', loc="center", fontsize=50)
        ax.set_xlabel('Product Category')
        ax.set_ylabel('Number of Orders')
        ax.tick_params(axis='x', labelsize=35)
        ax.tick_params(axis='y', labelsize=30)
        st.pyplot(fig)

        st.markdown("""
            \n
            **Exploration**
                    
            From our analysis of product categories, it's clear that the item people order the most is 'bed_bath_table,' racking up more than nine thousand orders. The runners-up are 'health_beauty' and 'sport_leisure,' each getting over seven thousand orders. This tells us that in Brazil, folks are really into products for home and personal care, as well as things related to sports and leisure. Businesses could use this info to plan their marketing and make sure they have enough stock of these popular items.    
        """)

        colors2 = ["#D3D3D3", "#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

        st.header("Payment Type Analysis")
        payment_data = create_by_paymenttype(all_order_df)
        most_used = all_order_df.payment_type.mode().iloc[0]
        st.metric("Most Used Payment Type", value=most_used)

        fig, ax = plt.subplots(figsize=(40, 10))
        sns.barplot(
            y = 'average_value',
            x = 'payment_type',
            data = payment_data,
            palette = colors2,
            ax = ax
        )

        ax.set_title("Average Payment Value by Payment Type", loc="center", fontsize=50)
        ax.set_ylabel(None)
        ax.set_xlabel(None)
        ax.tick_params(axis='x', labelsize=35)
        ax.tick_params(axis='y', labelsize=30)
        st.pyplot(fig)

        st.markdown("""\n
            **Exploration**
                    
            Looking at how people pay for their purchases, most people like using credit cards the most. They not only use it the most often but also spend the most money with it on average. Surprisingly, even though fewer people use debit cards (except for cases where the payment type is not defined), those who do spend a good amount. Now, vouchers are not the least popular, but they usually involve smaller transactions compared to other payment methods.
        """)

if explain_button:
    st.title("Explanatory Data Analysis")

    tab_titles = ['First Business Question', 'Second Business Question']
    tab1, tab2 = st.tabs(tab_titles)

    with tab1:
        st.header("Identifying the city that corresponds to the highest volume of orders for each review score.")
        review_data = create_by_review(all_order_df)

        most_popular_city_review = review_data.most_popular_city.mode().iloc[0]
        st.metric("Most Popular City for Customer", value=most_popular_city_review)

        fig, ax = plt.subplots(figsize=(40, 10))
        colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#90CAF9"]

        sns.barplot(
            y = 'total_sales',
            x = 'review_score',
            data = review_data,
            palette = colors,
            ax = ax
        )

        ax.set_title("Number of Total Sales by Review Score", loc="center", fontsize=50)
        ax.set_ylabel("Total Sales")
        ax.set_xlabel("Review Score")
        ax.tick_params(axis='x', labelsize=35)
        ax.tick_params(axis='y', labelsize=30)
        st.pyplot(fig)

        st.markdown("""
            **Explanation**
                    
            Analyzing the ecommerce platform's order data, São Paulo is the top city for buying things. Interestingly, customers frequently rate sellers with a perfect score of 5.0, correlating with higher total payment values. Conversely, the 2.0 score, which is the least favored, aligns with the lowest payment value. On the other hand, a 1.0 score is the third-highest, showing that customers don't mind giving the lowest rating.
        """)

        st.subheader("The Heatmap")

        plt.style.use("fivethirtyeight")
        fig, ax = plt.subplots(figsize=(25, 10))
        numeric_columns = all_order_df.select_dtypes(include=['float64', 'int64'])
        dataplot = sns.heatmap(numeric_columns.corr(), cmap="YlGnBu", annot=True, ax=ax)
        st.pyplot(fig)

        st.markdown("Moreover, a heatmap analysis reveals a positive correlation between payment installments and payment value. As the payment value increases, customers are more inclined to opt for installment payments. This suggests that higher-value transactions often involve the utilization of installment payment plans.")

    with tab2:
        st.header("How can the platform enhance the presentation of products, especially in categories with fewer photos, to improve the overall shopping experience and potentially boost sales?")
        product_data = create_by_photoqty(all_product_df)

        most_popular_city = product_data.most_popular_city.mode().iloc[0]
        st.metric("Most Popular City for Seller", value=most_popular_city)

        fig, ax = plt.subplots(figsize=(40, 20))
        sns.barplot(
            y = 'total_sales',
            x = 'product_photos_qty',
            data = product_data,
            ax = ax
        )

        ax.set_title("Number of Total Sales by Photos Quantity", loc="center", fontsize=50)
        ax.set_ylabel("Total Sales")
        ax.set_xlabel("Photos Quantity")
        ax.tick_params(axis='x', labelsize=35)
        ax.tick_params(axis='y', labelsize=30)
        st.pyplot(fig)

        st.markdown("""
            **Exploration**
                    
            It can be observed that a majority of products on the platform have a relatively low number of displayed photos. Specifically, the product category with the fewest photos is bed, bath, and table. To make the shopping experience better and sell more, the platform can focus on showing more and better-quality pictures of these products. By doing this, they can catch the attention of customers, make them more interested, and potentially increase sales.
        """)

        st.subheader("The Heatmap")

        plt.style.use("fivethirtyeight")
        fig, ax = plt.subplots(figsize=(25, 10))
        numeric_columns = all_product_df.select_dtypes(include=['float64', 'int64'])
        dataplot = sns.heatmap(numeric_columns.corr(), cmap="YlGnBu", annot=True, ax=ax)
        st.pyplot(fig)

        st.markdown("Furthermore, the heatmap analysis suggests that there is a positive relationship between the length of a product's description and its price. Products with longer descriptions tend to command higher prices. This observation opens up possibilities for strategic pricing and product description optimization, potentially influencing buyer behavior and sales performance.")
