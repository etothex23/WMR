import tkinter as tk
from tkinter import scrolledtext

def send_message():
    user_input = entry.get()
    if user_input:
        chat_display.insert(tk.END, f"You: {user_input}\n")
        # This is where we will later plug in the AI logic
        chat_display.insert(tk.END, f"Genie: I'm history! No, I'm mythology! Fine, I'm a bot.\n\n")
        entry.delete(0, tk.END)

# Create the main window
root = tk.Tk()
root.title("Templeton's AI Hub")

# Create chat display
chat_display = scrolledtext.ScrolledText(root, width=50, height=20)
chat_display.pack(padx=10, pady=10)

# Create entry box
entry = tk.Entry(root, width=40)
entry.pack(side=tk.LEFT, padx=10, pady=10)

# Create send button
send_btn = tk.Button(root, text="Send", command=send_message)
send_btn.pack(side=tk.RIGHT, padx=10)

root.mainloop()