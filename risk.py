import tkinter as tk
from tkinter import messagebox

def calculate_size():
    try:
        # Inputs
        exchange_rate = float(exchange_rate_entry.get())  # INR to USD conversion rate
        portfolio_value_inr = float(portfolio_value_entry.get())  # Portfolio value in INR
        avg_win_inr = float(avg_win_entry.get())  # Avg win in INR
        max_loss_inr = float(max_loss_entry.get())  # Max loss in INR
        last_loss_inr = float(last_loss_entry.get())  # Last loss in INR

        entry_price_inr = float(entry_price_inr_entry.get())  # Entry Price in INR
        stop_loss_inr = float(stop_loss_inr_entry.get())  # Stop Loss in INR

        market_price = float(market_price_entry.get())  # Market price in USD
        stop_loss = float(stop_loss_entry.get())  # Stop loss in USD

        # Convert INR values to USD
        avg_win = avg_win_inr / exchange_rate
        max_loss = max_loss_inr / exchange_rate
        last_loss = last_loss_inr / exchange_rate
        portfolio_value = portfolio_value_inr / exchange_rate

        entry_price = entry_price_inr / exchange_rate  # Convert Entry Price to USD
        stop_loss_usd = stop_loss_inr / exchange_rate  # Convert Stop Loss to USD

        # Determine trade type (Long or Short)
        if stop_loss < market_price:
            trade_type = "Long"
            risk_per_unit = market_price - stop_loss
        elif stop_loss > market_price:
            trade_type = "Short"
            risk_per_unit = stop_loss - market_price
        else:
            messagebox.showerror("Error", "Stop-loss cannot be equal to market price.")
            return

        # Adjust max loss dynamically with an EMA-like factor
        alpha = 0.3  # Weight given to last loss impact
        if avg_win < last_loss < max_loss:
            adjusted_max_loss = (1 - alpha) * max_loss + alpha * last_loss
        else:
            adjusted_max_loss = max_loss

        # Validate risk per unit
        if risk_per_unit <= 0:
            messagebox.showerror("Error", "Invalid stop-loss level.")
            return

        # Calculate trade size based on minimizing Updated Max Loss / Avg Win ratio
        target_risk = avg_win * 0.5
        initial_quantity = target_risk / risk_per_unit  # Allow fractional trades

        # **Adding Positions at Retracements**
        retracement_30 = entry_price + 0.3 * (stop_loss_usd - entry_price)
        retracement_50 = entry_price + 0.5 * (stop_loss_usd - entry_price)
        retracement_65 = entry_price + 0.65 * (stop_loss_usd - entry_price)

        # More weight to 65% retracement positions
        qty_30 = initial_quantity * 0.2  # 20% weight
        qty_50 = initial_quantity * 0.3  # 30% weight
        qty_65 = initial_quantity * 0.5  # 50% weight

        # Calculate total position size
        total_quantity = qty_30 + qty_50 + qty_65

        # **Expected Loss if SL is hit**
        avg_entry_price = (qty_30 * retracement_30 + qty_50 * retracement_50 + qty_65 * retracement_65) / total_quantity
        expected_loss = total_quantity * abs(avg_entry_price - stop_loss_usd)

        # Display results
        result_label.config(text=f"Trade Type: {trade_type}\n"
                                 f"Portfolio Value: ${portfolio_value:.2f}\n"
                                 f"Initial Trade Quantity: {initial_quantity:.4f}\n"
                                 f"Quantity at 30% Retracement: {qty_30:.4f} (Entry: ${retracement_30:.2f})\n"
                                 f"Quantity at 50% Retracement: {qty_50:.4f} (Entry: ${retracement_50:.2f})\n"
                                 f"Quantity at 65% Retracement: {qty_65:.4f} (Entry: ${retracement_65:.2f})\n"
                                 f"Total Quantity: {total_quantity:.4f}\n"
                                 f"Updated Max Loss/Average Win Ratio: {adjusted_max_loss / avg_win:.2f}\n"
                                 f"Expected Loss if SL is Hit: ${expected_loss:.2f}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# Create GUI window
root = tk.Tk()
root.title("Position Sizing Tool")
root.geometry("450x600")

# Inputs
tk.Label(root, text="Exchange Rate (INR to USD):").pack()
exchange_rate_entry = tk.Entry(root)
exchange_rate_entry.pack()

tk.Label(root, text="Portfolio Value (INR):").pack()
portfolio_value_entry = tk.Entry(root)
portfolio_value_entry.pack()

tk.Label(root, text="Latest Average Win (INR):").pack()
avg_win_entry = tk.Entry(root)
avg_win_entry.pack()

tk.Label(root, text="Maximum Loss (INR):").pack()
max_loss_entry = tk.Entry(root)
max_loss_entry.pack()

tk.Label(root, text="Last Loss Amount (INR):").pack()
last_loss_entry = tk.Entry(root)
last_loss_entry.pack()

tk.Label(root, text="Entry Price (INR):").pack()
entry_price_inr_entry = tk.Entry(root)
entry_price_inr_entry.pack()

tk.Label(root, text="Stop-Loss (INR):").pack()
stop_loss_inr_entry = tk.Entry(root)
stop_loss_inr_entry.pack()

tk.Label(root, text="Entry Price (USD):").pack()
market_price_entry = tk.Entry(root)
market_price_entry.pack()

tk.Label(root, text="Stop-Loss (USD):").pack()
stop_loss_entry = tk.Entry(root)
stop_loss_entry.pack()

# Calculate Button
tk.Button(root, text="Calculate", command=calculate_size).pack()

# Result Label
result_label = tk.Label(root, text="", fg="blue")
result_label.pack()

root.mainloop()
