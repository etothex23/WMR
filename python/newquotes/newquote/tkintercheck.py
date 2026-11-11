import tkinter as tk

def on_ok_click():
    """Handle OK button click."""
    print("OK clicked")

def on_reset_click():
    """Handle Reset button click."""
    print("Reset clicked")

def on_cancel_click():
    """Handle Cancel button click."""
    window.quit()  # Close the window
    window.destroy()  # Properly destroy the window

# Initialize the Tkinter window
window = tk.Tk()
window.title("Quote Entry")
window.geometry("400x200")

# Configure grid layout for the window
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=3)

# Create the label and entry for the Quote
quote_label = tk.Label(window, text="Quote:")
quote_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
quote_entry = tk.Entry(window, width=40)
quote_entry.grid(row=0, column=1, padx=10, pady=5)

# Create the label and entry for the Author
author_label = tk.Label(window, text="Author:")
author_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
author_entry = tk.Entry(window, width=40)
author_entry.grid(row=1, column=1, padx=10, pady=5)

# Create the label and entry for the Image
image_label = tk.Label(window, text="Image:")
image_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
image_entry = tk.Entry(window, width=40)
image_entry.grid(row=2, column=1, padx=10, pady=5)

# Create the button frame
button_frame = tk.Frame(window)
button_frame.grid(row=3, column=0, columnspan=2, pady=10)

# Create the OK button
ok_button = tk.Button(button_frame, text="OK", command=on_ok_click)
ok_button.grid(row=0, column=0, padx=10)

# Create the Reset button
reset_button = tk.Button(button_frame, text="Reset", command=on_reset_click)
reset_button.grid(row=0, column=1, padx=10)

# Create the Cancel button
cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel_click)
cancel_button.grid(row=0, column=2, padx=10)

# Run the Tkinter main loop
window.mainloop()