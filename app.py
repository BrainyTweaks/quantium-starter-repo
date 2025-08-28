# app.py

# Step 1: Imports
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

# Define color palette for regions
region_colors = {
    'north': '#FF6B6B',  # Coral red
    'east': '#4ECDC4',   # Turquoise
    'south': '#FFE66D',  # Yellow
    'west': '#6A0572',   # Purple
    'all': '#1A535C'     # Dark teal
}

# Step 3: Build Dash layout with region filter
app = dash.Dash(__name__)
app.title = "Soul Foods Sales Visualiser"

# Define CSS styles
styles = {
    'container': {
        'fontFamily': 'Arial, sans-serif',
        'backgroundColor': '#f8f9fa',
        'padding': '20px',
        'minHeight': '100vh'
    },
    'header': {
        'textAlign': 'center',
        'color': '#2c3e50',
        'marginBottom': '20px',
        'fontSize': '2.5rem',
        'fontWeight': 'bold',
        'textShadow': '2px 2px 4px rgba(0,0,0,0.1)'
    },
    'description': {
        'width': '80%',
        'margin': '0 auto 30px auto',
        'textAlign': 'center',
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
        'borderLeft': '5px solid #6A0572'
    },
    'filter-container': {
        'textAlign': 'center',
        'marginBottom': '30px',
        'backgroundColor': 'white',
        'padding': '20px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
        'borderLeft': '5px solid #4ECDC4'
    },
    'radio-items': {
        'display': 'inline-block',
        'margin': '0 15px',
        'fontSize': '1.1rem',
        'fontWeight': '500'
    },
    'graph-container': {
        'backgroundColor': 'white',
        'padding': '25px',
        'borderRadius': '10px',
        'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
        'borderLeft': '5px solid #FF6B6B'
    },
    'region-label': {
        'padding': '8px 15px',
        'borderRadius': '20px',
        'margin': '5px',
        'display': 'inline-block',
        'fontWeight': 'bold',
        'color': 'white'
    }
}

app.layout = html.Div(style=styles['container'], children=[
    html.H1("Soul Foods Pink Morsel Sales Visualiser", style=styles['header']),
    
    html.Div(style=styles['description'], children=[
        html.P("This visualization shows the sales trend of Pink Morsels over time across different regions."),
        html.P("The red dashed line indicates the price increase on January 15, 2021."),
        html.P("Based on the data, sales were HIGHER AFTER the price increase.", 
               style={'fontWeight': 'bold', 'color': '#27ae60', 'fontSize': '1.2rem'})
    ]),
    
    html.Div(style=styles['filter-container'], children=[
        html.H3("Filter by Region:", style={'marginBottom': '15px', 'color': '#2c3e50'}),
        dcc.RadioItems(
            id='region-radio',
            options=[
                {'label': html.Span(['All Regions'], style={'color': region_colors['all']}), 'value': 'all'},
                {'label': html.Span(['North'], style={'color': region_colors['north']}), 'value': 'north'},
                {'label': html.Span(['East'], style={'color': region_colors['east']}), 'value': 'east'},
                {'label': html.Span(['South'], style={'color': region_colors['south']}), 'value': 'south'},
                {'label': html.Span(['West'], style={'color': region_colors['west']}), 'value': 'west'}
            ],
            value='all',
            labelStyle=styles['radio-items'],
            inputStyle={'marginRight': '8px'}
        )
    ]),
    
    html.Div([
        html.H4("Region Colors:", style={'textAlign': 'center', 'marginBottom': '10px'}),
        html.Div([
            html.Span("North", style={**styles['region-label'], 'backgroundColor': region_colors['north']}),
            html.Span("East", style={**styles['region-label'], 'backgroundColor': region_colors['east']}),
            html.Span("South", style={**styles['region-label'], 'backgroundColor': region_colors['south']}),
            html.Span("West", style={**styles['region-label'], 'backgroundColor': region_colors['west']}),
            html.Span("All", style={**styles['region-label'], 'backgroundColor': region_colors['all']})
        ], style={'textAlign': 'center', 'marginBottom': '20px'})
    ]),
    
    html.Div(style=styles['graph-container'], children=[
        dcc.Graph(id='sales-line-chart')
    ])
])

# Step 4: Add callback for region filtering
@app.callback(
    Output('sales-line-chart', 'figure'),
    Input('region-radio', 'value')
)
def update_chart(selected_region):
    if df.empty:
        return px.line(title='No data available')
    
    # Filter data based on selected region
    if selected_region == 'all':
        # Show all regions with different colors
        fig = px.line(
            df,
            x='date',
            y='Sales',
            color='region',
            title='Pink Morsel Sales Over Time - All Regions',
            labels={'Sales': 'Total Sales (USD)', 'date': 'Date', 'region': 'Region'},
            color_discrete_map=region_colors
        )
    else:
        filtered_df = df[df['region'] == selected_region]
        title = f'Pink Morsel Sales Over Time - {selected_region.title()} Region'
        
        # Create the figure with specific region color
        fig = px.line(
            filtered_df,
            x='date',
            y='Sales',
            title=title,
            labels={'Sales': 'Total Sales (USD)', 'date': 'Date'}
        )
        
        # Update line color for single region
        fig.update_traces(line=dict(color=region_colors[selected_region], width=3))
    
    # Add vertical line for price increase
    price_increase_date = pd.to_datetime('2021-01-15')
    
    # Use the max sales value for the y1 parameter
    y_max = df['Sales'].max() if selected_region == 'all' else df[df['region'] == selected_region]['Sales'].max()
    
    fig.add_shape(
        type="line",
        x0=price_increase_date,
        y0=0,
        x1=price_increase_date,
        y1=y_max,
        line=dict(color="red", width=2, dash="dash")
    )
    
    # Add annotation for the price increase
    fig.add_annotation(
        x=price_increase_date,
        y=y_max * 0.9,
        text="Price Increase (Jan 15, 2021)",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40,
        bgcolor="white",
        bordercolor="red",
        borderwidth=1
    )
    
    # Update layout for better appearance
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#2c3e50', size=14),
        hovermode='x unified',
        legend=dict(
            title="Region",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(
        gridcolor='rgba(0,0,0,0.1)',
        title_font=dict(size=16)
    )
    
    fig.update_yaxes(
        gridcolor='rgba(0,0,0,0.1)',
        title_font=dict(size=16)
    )
    
    return fig

# Run the app
if __name__ == '__main__':
    print("Starting server...")
    print("Open http://localhost:8050 in your browser")
    app.run(debug=True, port=8050)