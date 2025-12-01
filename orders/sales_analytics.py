import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

SALES_FILE = Path(__file__).parent.parent / "data" / "sales_orders.csv"
INVENTORY_FILE = Path(__file__).parent.parent / "data" / "laptop_inventory.csv"


def _load_sales():
    if not SALES_FILE.exists():
        return pd.DataFrame(columns=['order_id', 'order_date', 'product_id', 'quantity'])
    df = pd.read_csv(SALES_FILE, dtype={'product_id': str})
    # parse dates (orders may be stored as date or datetime)
    df['order_date'] = pd.to_datetime(df.get('order_date', None), errors='coerce')
    df['quantity'] = pd.to_numeric(df.get('quantity', 0), errors='coerce').fillna(0).astype(int)
    return df


def _load_inventory():
    if not INVENTORY_FILE.exists():
        return pd.DataFrame()
    inv = pd.read_csv(INVENTORY_FILE, dtype={'product_id': str})
    return inv


def plot_sales_trend(df, ax=None):
    if df.empty:
        ax = ax or plt.gca()
        ax.text(0.5, 0.5, 'No sales data', ha='center')
        return
    s = df.set_index('order_date').resample('ME').quantity.sum()
    ax = ax or plt.gca()
    s.plot(ax=ax, marker='o')
    ax.set_title('Monthly Sales Quantity')
    ax.set_xlabel('Month')
    ax.set_ylabel('Quantity')


def plot_sales_by_product(df, inv_df, ax=None, top_n=10):
    if df.empty:
        ax = ax or plt.gca()
        ax.text(0.5, 0.5, 'No sales data', ha='center')
        return
    byp = df.groupby('product_id').quantity.sum().reset_index()
    if not inv_df.empty:
        byp = byp.merge(inv_df[['product_id', 'product']], on='product_id', how='left')
        byp['label'] = byp['product'].fillna(byp['product_id'])
    else:
        byp['label'] = byp['product_id']
    byp = byp.sort_values('quantity', ascending=False).head(top_n)
    ax = ax or plt.gca()
    ax.barh(byp['label'][::-1], byp['quantity'][::-1], color='C1')
    ax.set_title(f'Top {top_n} Products by Quantity')
    ax.set_xlabel('Quantity')


def plot_seasonality(df, ax=None):
    if df.empty:
        ax = ax or plt.gca()
        ax.text(0.5, 0.5, 'No sales data', ha='center')
        return
    df['month'] = df['order_date'].dt.month
    monthly = df.groupby('month').quantity.sum().reindex(range(1, 13), fill_value=0)
    ax = ax or plt.gca()
    ax.plot(monthly.index, monthly.values, marker='o')
    ax.set_xticks(range(1, 13))
    ax.set_title('Seasonality (Total by Month)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Quantity')


def show_dashboard(save_to_file=True):
    """Display sales dashboard and optionally save to file.
    
    Args:
        save_to_file (bool): If True, save the dashboard to 'dashboard.png' after showing.
    """
    df = _load_sales()
    inv = _load_inventory()

    # Use a style that's available in all matplotlib versions
    try:
        plt.style.use('seaborn-v0_8-whitegrid')
    except OSError:
        # Fallback to default if seaborn style not available
        plt.style.use('default')
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 8))
    ax_trend = axes[0, 0]
    ax_byprod = axes[0, 1]
    ax_season = axes[1, 0]
    # bottom-right: summary table
    ax_table = axes[1, 1]

    plot_sales_trend(df, ax_trend)
    plot_sales_by_product(df, inv, ax_byprod, top_n=8)
    plot_seasonality(df, ax_season)

    # summary: total orders, total qty, period
    total_orders = len(df)
    total_qty = int(df['quantity'].sum()) if not df.empty else 0
    min_date = df['order_date'].min()
    max_date = df['order_date'].max()
    period = f"{min_date.date()} - {max_date.date()}" if pd.notna(min_date) and pd.notna(max_date) else 'N/A'

    ax_table.axis('off')
    table_text = f"Total Orders: {total_orders}\nTotal Quantity: {total_qty}\nPeriod: {period}"
    ax_table.text(0.01, 0.5, table_text, va='center', fontsize=12)

    plt.tight_layout()
    
    # Show the dashboard
    plt.show()
    
    # Save to file after showing
    if save_to_file:
        try:
            output_path = Path(__file__).parent.parent / "dashboard.png"
            fig.savefig(output_path, dpi=150, bbox_inches='tight')
            print(f"Dashboard saved to {output_path}")
        except Exception as e:
            print(f"Warning: failed to save dashboard to file: {e}")


if __name__ == '__main__':
    show_dashboard()