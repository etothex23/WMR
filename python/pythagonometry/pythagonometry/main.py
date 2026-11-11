import math
import tkinter as tk

def calc_pythag():
    print("click")
    sides = adj_text_box.get("1.0", "end-1c")+','+opp_text_box.get("1.0", "end-1c")+','+hyp_text_box.get("1.0", "end-1c")
    triagnal(sides)
    points = [90, 10,
              90, 90,
              10, 10]
    canvas.delete("all")
    canvas.create_polygon(points, outline="red", fill="lightblue", width=2)

def triagnal(triangle):
    tri_list = triangle.split(',')
    print(tri_list)
    adj = tri_list[0]
    opp = tri_list[1]
    hyp = tri_list[2]
    which_side = 0
    for side in tri_list:
        if side.isdigit():
            #print(side)
            which_side+=1
        else:
            match which_side:
                case 0:  # adj
                    #print(side)
                    adj = math.sqrt(int(hyp) ** 2 - int(opp) ** 2)
                    adj_text_box.delete("1.0", "end")
                    adj_text_box.insert("1.0", str(adj))
                    print(adj)
                case 1:  # opp
                    #print(side)
                    opp = math.sqrt(int(hyp) ** 2 - int(adj) ** 2)
                    opp_text_box.delete("1.0", "end")
                    opp_text_box.insert("1.0", str(opp))
                    print(opp)
                case 2: # hyp
                    #print(side)
                    hyp = math.sqrt(int(adj) ** 2 + int(opp) ** 2)
                    hyp_text_box.delete("1.0", "end")
                    hyp_text_box.insert("1.0", str(hyp))
                    print(hyp)

root = tk.Tk()
root.title("Pythagorean Theorem")
points = [10, 90,
          10, 10,
          90, 10]
# Create and pack the first text box
adj_label = tk.Label(root, text="Adjacent:")
adj_text_box = tk.Text(root, height=2, width=10)
adj_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
adj_text_box.grid(row=0, column=1, padx=5, pady=5)

# Create and pack the first text box
opp_label = tk.Label(root, text="Opposite:")
opp_text_box = tk.Text(root, height=2, width=10)
opp_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
opp_text_box.grid(row=1, column=1, padx=5, pady=5)

# Create and pack the first text box
hyp_label = tk.Label(root, text="Hypotenuse:")
hyp_text_box = tk.Text(root, height=2, width=10)
hyp_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
hyp_text_box.grid(row=2, column=1, padx=5, pady=5)

btn_calc_pythag = tk.Button(root, text="Calculate", command=calc_pythag)
btn_calc_pythag.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")

canvas = tk.Canvas(root, width=100, height=100, bg="white")
canvas.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky="w")
canvas.create_polygon(points, outline="blue", fill="lightblue", width=2)

root.geometry("275x300")
# Start the Tkinter event loop
root.mainloop()