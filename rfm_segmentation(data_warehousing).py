# -*- coding: utf-8 -*-
"""RFM Segmentation(Data Warehousing).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w34hOC8FeCLf_-f30DYr2hbQ66zoXWGL
"""



"""**Performing RFM Segmentation on a Simple Grocery Dataset**
# *Customer Segementation and Analysis using RFM & K-means*
"""

# Import necessary libraries
import pandas as pd
import sqlite3

# Load the data into a pandas DataFrame
Groceries_df = pd.read_csv('Groceries_dataset.csv')

# Display the dataset
Groceries_df

# Checking for missing values in the data
missing_values = Groceries_df.isna().sum()
print("Missing Values:")
print(missing_values)


# Convert the Date attribute to a datetime object for processing
Groceries_df['Date'] = pd.to_datetime(Groceries_df['Date'], infer_datetime_format=True)
Groceries_df.head()

# Calculate the distribution of items purchased
item_distribution = Groceries_df['itemDescription'].value_counts().reset_index()
item_distribution.columns = ['itemDescription', 'count']

# Calculate the distribution of transactions per customer
transactions_per_customer = Groceries_df.groupby('Member_number')['Date'].nunique().reset_index()
transactions_per_customer.columns = ['Member_number', 'num_transactions']

# Print the first few rows of item_distribution
print("Item Distribution:")
print(item_distribution.head(5))

# Print the first few rows of transactions_per_customer
print("\nTransactions per Customer:")
print(transactions_per_customer.head(5))

# Visualizing the item distribution

import matplotlib.pyplot as plt
import seaborn as sns

top_items = item_distribution.head(10)
plt.figure(figsize=(10, 5))
sns.barplot(x='itemDescription', y='count', data=top_items, color='green')
plt.title('Top 10 Items Purchased')
plt.xlabel('Item')
plt.ylabel('Number of Purchases')
plt.xticks(rotation=45)
plt.show()

# Visualize the distribution of transactions per customer

plt.figure(figsize=(10, 5))
sns.histplot(transactions_per_customer['num_transactions'], kde=True, bins=20, color='blue')
plt.title('Distribution of Transactions per Customer')
plt.xlabel('Number of Transactions')
plt.ylabel('Frequency')
plt.show()

import numpy as np
# Calculate the total number of customers
total_customers = len(transactions_per_customer)

# Calculate basic statistics for the original data
Groceries_df['Date'].describe()

# Calculate statistical analysis for transactions per customer
transactions = transactions_per_customer['num_transactions'].describe()

transactions

# Grouping the data by Date and counting the number of transactions for each date and printing the results below
transactions_per_day = Groceries_df.groupby('Date').size().reset_index(name='num_transactions')
average_transactions_per_day = transactions_per_day['num_transactions'].mean()

print("Average number of transactions per day:", average_transactions_per_day)

# Connect to a SQLite3 database
conn = sqlite3.connect('Groceries_RFM.db' )
cur = conn.cursor()

# Write the cleaned DataFrame to a new table in the newly created database
Groceries_df.to_sql('Transactions', conn, if_exists='replace', index=False)

import matplotlib.pyplot as plt
import seaborn as sns

# Group the data by Date and count the number of purchases for each date
purchases_by_date = Groceries_df.groupby('Date').size().reset_index(name='num_purchases')

# Create a time series plot of the total number of purchases by date
plt.figure(figsize=(12, 6))
sns.lineplot(x='Date', y='num_purchases', data=purchases_by_date)
plt.title('Total Number of Purchases Per Day')
plt.xlabel('Date')
plt.ylabel('Number of Purchases')
plt.show()

num_users = Groceries_df['Member_number'].nunique()
print(f"Number of unique users: {num_users}")


num_itemsxxc = Groceries_df['itemDescription'].nunique()
print(f"Number of unique Items: {num_itemsxxc}")

import matplotlib.pyplot as plt
import seaborn as sns

# Group the data by Date and count the number of purchases for each date
purchases_by_date =  Groceries_df.groupby('Date').size().reset_index(name='num_purchases')

# Set Date as index and resample to weekly frequency
purchases_by_date.set_index('Date', inplace=True)
purchases_by_week = purchases_by_date.resample('W').sum().reset_index()

# Create a time series plot of the total number of purchases by week
plt.figure(figsize=(12, 6))
sns.lineplot(x='Date', y='num_purchases', data=purchases_by_week)
plt.title('Total Number of Purchases Per Day Shown by Weeks')
plt.xlabel('Week')
plt.ylabel('Number of Purchases')
plt.show()

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Group the data by Date and count the number of purchases for each date
purchases_by_date =  Groceries_df.groupby('Date').size().reset_index(name='num_purchases')

# Set Date as index and resample to monthly frequency
purchases_by_date.set_index('Date', inplace=True)
purchases_by_month = purchases_by_date.resample('M').sum().reset_index()

# Create a time series plot of the total number of purchases by month
plt.figure(figsize=(12, 6))
ax = sns.lineplot(x='Date', y='num_purchases', data=purchases_by_month)
plt.title('Total Number of Purchases Per Day Shown by Month')
plt.xlabel('Month')
plt.ylabel('Number of Purchases')

plt.show()

import datetime
# Set the analysis date (use the latest date in the dataset + 1 day)
date =  Groceries_df['Date'].max() + datetime.timedelta(days=1)

# SQL query to calculate Recency, Frequency, and Monetary values for each customer
rfm_query = '''
SELECT
  Member_number,
  julianday('2015-12-31') - julianday(MAX(Date)) AS Recency,
  COUNT(DISTINCT Date) AS Frequency,
  COUNT(*) AS Monetary
FROM
  Transactions
GROUP BY
  Member_number
'''

rfm_data = pd.read_sql_query(rfm_query, conn)

# Display the first 10 rows of the RFM DataFrame
print(rfm_data.head(10))

selected_members = rfm_data[rfm_data['Member_number'].isin([1024, 1090])]
print(selected_members)

member_1090_frequency = rfm_data.loc[rfm_data['Member_number'] == 1090, 'Frequency'].iloc[0]
print(f"Member 1090 bought items {member_1090_frequency} times.")

# Assign RFM scores for Recency, Frequency, and Monetary
rfm_data['Recency_Score'] = pd.qcut(rfm_data['Recency'], 4, labels=list(range(4, 0, -1)))
rfm_data['Frequency_Score'] = pd.qcut(rfm_data['Frequency'], 4, labels=list(range(1, 5)))
rfm_data['Monetary_Score'] = pd.qcut(rfm_data['Monetary'], 4, labels=list(range(1, 5)))

# Concatenate RFM scores as strings
rfm_data['RFM_Score'] = rfm_data['Recency_Score'].astype(str) + rfm_data['Frequency_Score'].astype(str) + rfm_data['Monetary_Score'].astype(str)

# Define a function to categorize members based on their RFM scores
def rfm_level(df):
    if df['RFM_Score'] == '444':
        return 'Best Customers'
    elif df['RFM_Score'][0] >= '3' and df['RFM_Score'][1] >= '3' and df['RFM_Score'][2] >= '3':
        return 'Loyal'
    elif df['RFM_Score'][0] >= '3' and df['RFM_Score'][1] >= '1' and df['RFM_Score'][2] >= '2':
        return 'Potential Loyalist'
    elif df['RFM_Score'][0] >= '3' and df['RFM_Score'][1] >= '1' and df['RFM_Score'][2] >= '1':
        return 'Promising'
    elif df['RFM_Score'][0] >= '2' and df['RFM_Score'][1] >= '2' and df['RFM_Score'][2] >= '2':
        return 'Customers Needing Attention'
    elif df['RFM_Score'][0] >= '1' and df['RFM_Score'][1] >= '2' and df['RFM_Score'][2] >= '2':
        return 'At Risk'
    elif df['RFM_Score'][0] >= '1' and df['RFM_Score'][1] >= '1' and df['RFM_Score'][2] >= '2':
        return 'Hibernating'
    else:
        return 'Lost'

# Apply the function to the RFM DataFrame
rfm_data['RFM_Level'] = rfm_data.apply(rfm_level, axis=1)

# Display the first 10 rows of the RFM DataFrame
print(rfm_data.head(10))

# Count the number of customers in each RFM level
rfm_level_counts = rfm_data.groupby('RFM_Level')['Member_number'].count().reset_index()

# Plot pie chart with annotated labels
fig, ax = plt.subplots(figsize=(10, 6))
ax.pie(
    rfm_level_counts['Member_number'],
    labels=rfm_level_counts['RFM_Level'],
    autopct='%1.1f%%',
    startangle=90,
    counterclock=False
)
ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular
plt.title('Distribution of Customers by RFM Level')
plt.show()

# Count the number of customers in each RFM level
rfm_level_counts = rfm_data.groupby('RFM_Level')['Member_number'].count().reset_index()

# Define colors for each RFM level
colors = ['royalblue', 'mediumseagreen', 'gold', 'firebrick', 'darkviolet']

# Create a column chart with different colors for each bar
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(
    rfm_level_counts['RFM_Level'],
    rfm_level_counts['Member_number'],
    color=colors
)

# Add labels and formatting
plt.title('Distribution of Customers by RFM Level')
plt.xlabel('RFM Level')
plt.ylabel('Number of Customers')
plt.xticks(rotation=90)

# Annotate the bars with the number of customers
for i, v in enumerate(rfm_level_counts['Member_number']):
    ax.text(i, v + 5, str(v), ha='center')


plt.show()

# Create a bar chart for the distribution of customers by RFM level
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(
    rfm_level_counts['RFM_Level'],
    rfm_level_counts['Member_number'],
    color='dodgerblue'
)

# Add labels and title
plt.xlabel('RFM Level')
plt.ylabel('Number of Customers')
plt.title('Distribution of Customers by RFM Level')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Annotate the bars with the number of customers
for i, v in enumerate(rfm_level_counts['Member_number']):
    ax.text(i, v + 5, str(v), ha='center')

plt.show()

# Sort the rfm_level_counts DataFrame by the number of customers in descending order
rfm_level_counts_sorted = rfm_level_counts.sort_values('Member_number', ascending=False)

# Create a bar chart for the distribution of customers by RFM level
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(
    rfm_level_counts_sorted['RFM_Level'],
    rfm_level_counts_sorted['Member_number'],
    color='dodgerblue'
)

# Add labels and title
plt.xlabel('RFM Level')
plt.ylabel('Number of Customers')
plt.title('Distribution of Customers by RFM Level')

# Rotate x-axis labels for better readability
plt.xticks(rotation=45)

# Annotate the bars with the number of customers
for i, v in enumerate(rfm_level_counts_sorted['Member_number']):
    ax.text(i, v + 5, str(v), ha='center')

plt.show()

import seaborn as sns
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
sns.histplot(data=rfm_data, x='Recency', kde=True)
ax.set_title('Histogram and Recency')

import seaborn as sns
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
sns.histplot(data=rfm_data, x='Frequency', kde=True)
ax.set_title('Histogram and Frequency')

import seaborn as sns
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
sns.histplot(data=rfm_data, x='Monetary', kde=True)
ax.set_title('Histogram and MonetaryValue')

import seaborn as sns
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(12, 4))

sns.histplot(data=rfm_data, x='Recency', kde=True, ax=axes[0])
sns.histplot(data=rfm_data, x='Frequency', kde=True, ax=axes[1])
sns.histplot(data=rfm_data, x='Monetary', kde=True, ax=axes[2])

axes[0].set_title('Histogram of Recency')
axes[1].set_title('Histogram of Frequency')
axes[2].set_title('Histogram of MonetaryValue')

plt.show()

from sklearn.preprocessing import StandardScaler

# Extract the RFM features
rfm_features = rfm_data[['Recency', 'Frequency', 'Monetary']]

# Scale the RFM features
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm_features)

# Transforming the RFM table

# Imports the "stats" module from the "scipy" library and creates an empty pandas DataFrame named "Members_fix". 
# Applies the Box-Cox transformation to the "Recency", "Frequency", and "MonetaryValue" 
# columns of the "Members" DataFrame, and stores the transformed data in "Members_fix". Prints the last five rows of "Members_fix".


# Creates a new figure with a size of 12x10 and creates three subplots to display the distribution of the transformed "Recency", "Frequency", and "MonetaryValue" columns 
# using the seaborn "distplot" function. Displays the plot.

from scipy import stats
Members_rfm_data= pd.DataFrame()

Members_rfm_data["Recency"], _ = stats.boxcox(rfm_data['Recency'] + 1)  # add 1 to ensure data is positive
Members_rfm_data["Frequency"], _ = stats.boxcox(rfm_data['Frequency'] + 1)
Members_rfm_data["Monetary"], _ = stats.boxcox(rfm_data['Monetary'] + 1)
Members_rfm_data.tail()

# Plot RFM distributions
plt.figure(figsize=(12,10))
# Plot distribution of R
plt.subplot(3, 1, 1); sns.distplot(Members_rfm_data['Recency'])
# Plot distribution of F
plt.subplot(3, 1, 2); sns.distplot(Members_rfm_data['Frequency'])
# Plot distribution of M
plt.subplot(3, 1, 3); sns.distplot(Members_rfm_data['Monetary'])
# Show the plot
plt.show()

# Import library
from sklearn.preprocessing import StandardScaler
# Initialize the Object
scaler = StandardScaler()
# Fit and Transform The Data
scaler.fit(Members_rfm_data)

rfm_data_normalized = scaler.transform(Members_rfm_data)
# Assert that it has mean 0 and variance 1
print(rfm_data_normalized.mean(axis = 0).round(2)) # [0. -0. 0.]
print(rfm_data_normalized.std(axis = 0).round(2)) # [1. 1. 1.]

from sklearn.cluster import KMeans
sse = {}
for k in range(1, 11):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(rfm_data_normalized)
    sse[k] = kmeans.inertia_ # SSE to closest cluster centroid
plt.title('The Elbow Method')
plt.xlabel('k')
plt.ylabel('SSE')
sns.pointplot(x=list(sse.keys()), y=list(sse.values()))
plt.show()

from yellowbrick.cluster import KElbowVisualizer
from sklearn.cluster import KMeans
model = KMeans()
visualizer = KElbowVisualizer(model, k=(1,12))
visualizer.fit(rfm_data_normalized)  
visualizer.show()

model = KMeans(n_clusters=4, random_state=42)
model.fit(rfm_data_normalized)
model.labels_.shape
rfm_data["Cluster"] = model.labels_
rfm_data.groupby('Cluster').agg({
    'Recency':'mean',
    'Frequency':'mean',
    'Monetary':['mean', 'count']}).round(2)
f, ax = plt.subplots(figsize=(25, 5))
ax = sns.countplot(x="Cluster", data=rfm_data)
rfm_data.groupby(['Cluster']).count()

rfm_data["Cluster"] = model.labels_
rfm_data.groupby('Cluster').agg({
    'Recency':'mean',
    'Frequency':'mean',
    'Monetary':['mean', 'count']}).round(2)

# Create the dataframe
df_normalized = pd.DataFrame(rfm_data_normalized, columns=['Recency', 'Frequency', 'Monetary'])
df_normalized['ID'] = rfm_data.index
df_normalized['Cluster'] = model.labels_
# Melt The Data
df_nor_melt = pd.melt(df_normalized.reset_index(),
                      id_vars=['ID', 'Cluster'],
                      value_vars=['Recency','Frequency','Monetary'],
                      var_name='Attribute',
                      value_name='Value')
df_nor_melt.head()
# Visualize it
sns.lineplot(x = 'Attribute', y= 'Value', hue='Cluster', data=df_nor_melt)

# Count the number of users in each RFM label
rfm_label_counts = rfm_data['RFM_Level'].value_counts()

# Convert the Series to a DataFrame
rfm_label_counts_df = rfm_label_counts.reset_index()

# Rename the columns
rfm_label_counts_df.columns = ['RFM_Level', 'Number_of_Users']

# Display the table
print(rfm_label_counts_df)

!pip install squarify


import squarify
import matplotlib.pyplot as plt
import seaborn as sns

# Calculate the proportion of each RFM label
label_proportions = rfm_data['RFM_Level'].value_counts(normalize=True) * 100

# Define a color palette with different colors for each label
colors = sns.color_palette('husl', n_colors=len(label_proportions))

# Create the treemap plot
fig, ax = plt.subplots(figsize=(12, 8))
squarify.plot(sizes=label_proportions.values, label=label_proportions.index, color=colors, alpha=0.8, ax=ax)

# Set the title and remove the axis
ax.set_title('RFM Segments')
plt.axis('off')
plt.show()

from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

# Prepare the data for clustering (select relevant columns and normalize)
X = rfm_data[['Recency', 'Frequency', 'Monetary']]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split the data into training (80%) and testing (20%) sets
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)

# Train the K-means model using the optimal k value (in this case, k=2)
kmeans = KMeans(n_clusters=2, random_state=42)
kmeans.fit(X_train)

# Predict cluster labels for the testing set
y_pred = kmeans.predict(X_test)

# Evaluate the performance of the model using silhouette score
score = silhouette_score(X_test, y_pred)
print(f"Silhouette Score: {score:.2f}")

"""**EXPERIMENTATION COMPLETED**"""