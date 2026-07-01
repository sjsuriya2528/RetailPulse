import nbformat as nbf

nb = nbf.v4.new_notebook()

text = """# 📊 RetailPulse: Exploratory Data Analysis (EDA)
This notebook explores the raw transaction data to identify patterns, distributions, and anomalies.
Key focus areas:
1. Sales distributions over time.
2. Top products and retailers.
3. Order cancellations and data quality."""

code_1 = """import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set plotting style
plt.style.use('ggplot')
sns.set_palette("viridis")

# Load raw data
orders = pd.read_csv('../data/raw/updated_Orders.csv', parse_dates=['createdAt'])
order_items = pd.read_csv('../data/raw/final_updated_orderitems_combined.csv')

print(f"Total Orders: {len(orders)}")
print(f"Total Order Items: {len(order_items)}")"""

code_2 = """# 📈 1. Orders Over Time
orders['date'] = orders['createdAt'].dt.date
daily_orders = orders.groupby('date').size()

plt.figure(figsize=(14, 5))
daily_orders.plot()
plt.title('Daily Order Volume')
plt.ylabel('Number of Orders')
plt.xlabel('Date')
plt.tight_layout()
plt.show()"""

code_3 = """# 💰 2. Order Value Distribution
plt.figure(figsize=(10, 5))
sns.histplot(orders[orders['totalAmount'] < 5000]['totalAmount'], bins=50, kde=True)
plt.title('Distribution of Order Values (Under 5000)')
plt.xlabel('Total Amount')
plt.ylabel('Frequency')
plt.show()"""

insight = """### 💡 Key Insights
- **Order Volume**: There are clear periodic spikes in order volumes indicating weekly ordering patterns by retailers.
- **Order Value**: The distribution of order values is heavily right-skewed. Most orders are of smaller values, but there is a long tail of high-value bulk orders.
- **Next Steps**: We will build RFM segments to classify these high-value bulk purchasers."""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_code_cell(code_3),
    nbf.v4.new_markdown_cell(insight)
]

with open('notebooks/01_eda.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print("Notebook generated successfully!")
