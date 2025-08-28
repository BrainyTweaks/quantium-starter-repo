# app.py

# Step 1: Imports
import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px

# Step 2: Load and prepare Pink Morsel sales data
try:
    df0 = pd.read_csv("data/daily_sales_data_0.csv")
    df1 = pd.read_csv("data/daily_sales_data_1.csv")
    df2 = pd.read_csv("data/daily_sales_data_2.csv")
    
    # Combine CSVs
    df = pd.concat([df0, df1, df2], ignore_index=True)
    
    # Keep only Pink Morsels (case insensitive)
    df = df[df['product'].str.lower() == "pink morsel"]
    
    # Clean price data - remove dollar signs and convert to float
    df['price'] = df['price'].str.replace('$', '').astype(float)
    
    # Create Sales column
    df['Sales'] = df['quantity'] * df['price']
    
    # Keep relevant columns
    df = df[['Sales', 'date', 'region']]
    
    # Convert date to datetime and remove invalid rows
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print("Data loaded successfully")
    print(f"Data range: {df['date'].min()} to {df['date'].max()}")
    print(f"Total sales records: {len(df)}")
    
except Exception as e:
    print(f"Error loading data: {e}")
    # Create empty dataframe if there's an error
    df = pd.DataFrame(columns=['Sales', 'date', 'region'])

# Step 3: Create the line chart
if not df.empty:
    fig = px.line(
        df,
        x='date',
        y='Sales',
        title='Pink Morsel Sales Over Time',
        labels={'Sales': 'Total Sales (USD)', 'date': 'Date'}
    )

    # Add vertical line for price increase
    price_increase_date = pd.to_datetime('2021-01-15')
    
    # Add the vertical line using a shape
    fig.add_shape(
        type="line",
        x0=price_increase_date,
        y0=0,
        x1=price_increase_date,
        y1=df['Sales'].max(),
        line=dict(color="red", width=2, dash="dash")
    )

    # Add annotation for the price increase
    fig.add_annotation(
        x=price_increase_date,
        y=df['Sales'].max() * 0.9,
        text="Price Increase (Jan 15, 2021)",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        bgcolor="white"
    )
else:
    # Create an empty figure if data loading failed
    fig = px.line(title='No data available')

# Step 4: Build Dash layout
app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

app.layout = html.Div([
    html.H1("Soul Foods Pink Morsel Sales Visualiser", 
            style={'textAlign': 'center', 'marginBottom': 20}),
    
    html.Div([
        html.P("This visualization shows the sales trend of Pink Morsels over time."),
        html.P("The red dashed line indicates the price increase on January 15, 2021."),
        html.P("Based on the data, sales were HIGHER AFTER the price increase.")
    ], style={'width': '80%', 'margin': '0 auto', 'textAlign': 'center', 'marginBottom': 30}),
    
    dcc.Graph(
        id='sales-line-chart',
        figure=fig
    )
])

# Run the app with specific port to avoid conflicts
if __name__ == '__main__':
    print("Starting server...")
    print("Open http://localhost:8050 in your browser")
    app.run(debug=True, port=8050)