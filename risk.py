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

        # Get selected currency
        selected_currency = currency_var.get()

        # Convert INR values to USD if needed
        avg_win_usd = avg_win_inr / exchange_rate
        max_loss_usd = max_loss_inr / exchange_rate
        last_loss_usd = last_loss_inr / exchange_rate
        portfolio_value_usd = portfolio_value_inr / exchange_rate

        # Handle entry price and stop-loss based on selected currency
        if selected_currency == "INR":
            entry_price = float(entry_price_entry.get())  # Entry Price in INR
            stop_loss = float(stop_loss_entry.get())  # Stop Loss in INR
            avg_win = avg_win_inr
            max_loss = max_loss_inr
            last_loss = last_loss_inr
            portfolio_value = portfolio_value_inr
        else:
            entry_price = float(entry_price_entry.get())  # Entry Price in USD
            stop_loss = float(stop_loss_entry.get())  # Stop Loss in USD
            avg_win = avg_win_usd
            max_loss = max_loss_usd
            last_loss = last_loss_usd
            portfolio_value = portfolio_value_usd

        # Determine trade type (Long or Short)
        if stop_loss < entry_price:
            trade_type = "Long"
            risk_per_unit = entry_price - stop_loss
        elif stop_loss > entry_price:
            trade_type = "Short"
            risk_per_unit = stop_loss - entry_price
        else:
            messagebox.showerror("Error", "Stop-loss cannot be equal to entry price.")
            return

        # Adjust max loss dynamically using a moving average approach
        alpha = 0.3  # Weight given to last loss impact
        if avg_win < last_loss < max_loss:
            adjusted_max_loss = (1 - alpha) * max_loss + alpha * last_loss
        else:
            adjusted_max_loss = max_loss

        # Validate risk per unit
        if risk_per_unit <= 0:
            messagebox.showerror("Error", "Invalid stop-loss level.")
            return

        # **Dynamic Risk Adjustment Based on ML/AW Ratio**
        ml_aw_ratio = adjusted_max_loss / avg_win
        if ml_aw_ratio <= 0.5:
            risk_multiplier = 2.0  # Aggressive increase in position size
        elif ml_aw_ratio <= 0.75:
            risk_multiplier = 1.75
        elif ml_aw_ratio <= 1.0:
            risk_multiplier = 1.5
        elif ml_aw_ratio <= 1.25:
            risk_multiplier = 1.25
        elif ml_aw_ratio <= 1.5:
            risk_multiplier = 1.0  # Standard size
        elif ml_aw_ratio <= 2.0:
            risk_multiplier = 0.75  # Reduce position size
        else:
            risk_multiplier = 0.5  # Strong reduction in risk

        # Adjusted position sizing based on risk dynamics
        target_risk = avg_win * risk_multiplier
        initial_quantity = target_risk / risk_per_unit  # Allow fractional trades

        # **Adding Positions at Retracements**
        retracement_30 = entry_price - (0.3 * (entry_price - stop_loss))
        retracement_50 = entry_price - (0.5 * (entry_price - stop_loss))
        retracement_65 = entry_price - (0.65 * (entry_price - stop_loss))

        # More weight to 65% retracement positions
        qty_30 = initial_quantity * 0.2  # 20% weight
        qty_50 = initial_quantity * 0.3  # 30% weight
        qty_65 = initial_quantity * 0.5  # 50% weight

        # Calculate total position size
        total_quantity = qty_30 + qty_50 + qty_65

        # **Expected Loss if SL is hit**
        avg_entry_price = (qty_30 * retracement_30 + qty_50 * retracement_50 + qty_65 * retracement_65) / total_quantity
        expected_loss = total_quantity * abs(avg_entry_price - stop_loss)

        # Convert expected loss to INR if trading in INR
        if selected_currency == "INR":
            expected_loss_text = f"₹{expected_loss:,.2f}"
        else:
            expected_loss_text = f"${expected_loss:,.2f}"

        # Display results
        result_label.config(text=f"Trade Type: {trade_type}\n"
                                 f"Portfolio Value: {('₹' if selected_currency == 'INR' else '$')}{portfolio_value:,.2f}\n"
                                 f"Initial Trade Quantity: {initial_quantity:.4f}\n"
                                 f"Quantity at 30% Retracement: {qty_30:.4f} (Entry: {retracement_30:,.2f})\n"
                                 f"Quantity at 50% Retracement: {qty_50:.4f} (Entry: {retracement_50:,.2f})\n"
                                 f"Quantity at 65% Retracement: {qty_65:.4f} (Entry: {retracement_65:,.2f})\n"
                                 f"Total Quantity: {total_quantity:.4f}\n"
                                 f"Updated Max Loss/Average Win Ratio: {ml_aw_ratio:.2f}\n"
                                 f"Risk Multiplier: {risk_multiplier:.2f}x\n"
                                 f"Expected Loss if SL is Hit: {expected_loss_text}")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numeric values.")

# Create GUI window
root = tk.Tk()
root.title("Position Sizing Tool")
root.geometry("500x600")

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

# Currency Selection Dropdown
tk.Label(root, text="Select Trading Currency:").pack()
currency_var = tk.StringVar(value="INR")
currency_dropdown = tk.OptionMenu(root, currency_var, "INR", "USD")
currency_dropdown.pack()

# Entry Price & Stop Loss based on selected currency
tk.Label(root, text="Entry Price:").pack()
entry_price_entry = tk.Entry(root)
entry_price_entry.pack()

tk.Label(root, text="Stop-Loss Level:").pack()
stop_loss_entry = tk.Entry(root)
stop_loss_entry.pack()

# Calculate Button
tk.Button(root, text="Calculate", command=calculate_size).pack()

# Result Label
result_label = tk.Label(root, text="", fg="blue")
result_label.pack()

root.mainloop()
