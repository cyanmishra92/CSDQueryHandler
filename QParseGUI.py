import re
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import json

def parse_select_query(query):
    # Regular expression patterns
    select_pattern = r"SELECT\s+(.*?)\s+FROM"
    where_pattern = r"WHERE\s+(.*)"

    # Extract SELECT and WHERE clauses from the query
    select_match = re.search(select_pattern, query, re.IGNORECASE)
    where_match = re.search(where_pattern, query, re.IGNORECASE)

    if not select_match:
        raise ValueError("Invalid query format. Please provide a valid SELECT query.")

    # Extract column names from the SELECT clause
    columns = [col.strip() for col in select_match.group(1).split(',')]

    if where_match:
        # Extract filter function and constants from the WHERE clause
        where_clause = where_match.group(1)
        where_parts = re.split(r"(AND|OR)", where_clause.strip())

        subfunctions = []
        jtypes = []
        for part in where_parts:
            part = part.strip()
            if part == "AND" or part == "OR":
                jtypes.append(part)
            else:
                function_parts = re.split(r"(>=|<=|!=|>|<|=)", part.strip())

                if len(function_parts) != 3:
                    raise ValueError("Invalid filter function format. Please provide a valid filter function.")

                subfunction = {
                    "Function": function_parts[0].strip(),
                    "Symbol": function_parts[1].strip(),
                    "Constant": function_parts[2].strip()
                }
                subfunctions.append(subfunction)

        return {
            "Output": columns,
            "TableName": "PAR_DATA",
            "Function": where_clause,
            "Subfunctions": len(subfunctions),
            "Functions": subfunctions,
            "JTypes": jtypes
        }
    else:
        return {
            "Output": columns
        }

def gui_interface():
    def parse_query():
        query = text_box.get("1.0", tk.END).strip()
        try:
            result = parse_select_query(query)
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Output: " + ', '.join(result['Output']) + "\n")
            output_text.insert(tk.END, "TableName: " + result['TableName'] + "\n")
            output_text.insert(tk.END, "Function: " + result['Function'] + "\n")
            output_text.insert(tk.END, "Subfunctions: " + str(result['Subfunctions']) + "\n")

            for i in range(result['Subfunctions']):
                function = result['Functions'][i]
                jtype = result['JTypes'][i] if i < len(result['JTypes']) else ""
                output_text.insert(tk.END, "Function-" + str(i+1) + ": " + function['Function'] + "\n")
                output_text.insert(tk.END, "Symbol-" + str(i+1) + ": " + function['Symbol'] + "\n")
                output_text.insert(tk.END, "Constant-" + str(i+1) + ": " + function['Constant'] + "\n")
                output_text.insert(tk.END, "JType-" + str(i+1) + ": " + jtype + "\n")
                output_text.insert(tk.END, "\n")

            output_text.pack(fill=tk.BOTH, expand=True)  # Adjust container size based on text

            # Save the parsed query to a JSON file
            with open('parsed_query.json', 'w') as file:
                json.dump(result, file)

        except Exception as e:
            output_text.delete("1.0", tk.END)
            output_text.insert(tk.END, "Error: " + str(e))

    def save_to_json():
        query = text_box.get("1.0", tk.END).strip()
        try:
            result = parse_select_query(query)
            with open("output.json", "w") as f:
                json.dump(result, f, indent=4)
            messagebox.showinfo("Save Successful", "Parsed query has been saved to output.json.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_help():
        help_text = "SELECT Query Parser Help:\n\n"
        help_text += "--gui: Use the GUI interface.\n"
        help_text += "--hlp: Show help information for the GUI.\n"
        help_text += "--sq: Start of the SELECT query (required).\n"
        help_text += "\nPlease enter the SELECT query in the text box and click 'Parse Query' to parse it."
        messagebox.showinfo("Help", help_text)

    window = tk.Tk()
    window.title("DB Engine")
    window.geometry("600x400")

    #window.iconbitmap("PSUCSDlogo.ico")
    window.tk.call('wm', 'iconphoto', window._w, tk.PhotoImage(file='PSUCSDlogo.gif'))

    style = ttk.Style(window)
    style.configure("TText", wrap="word")

    text_box = tk.Text(window, height=10, width=80)
    text_box.pack(pady=10)

    button_frame = tk.Frame(window)
    button_frame.pack()

    parse_button = tk.Button(button_frame, text="Parse Query", command=parse_query)
    parse_button.pack(side=tk.LEFT)

    save_button = tk.Button(button_frame, text="Save to JSON", command=save_to_json)
    save_button.pack(side=tk.LEFT)

    help_button = tk.Button(button_frame, text="Help", command=show_help)
    help_button.pack(side=tk.LEFT)

    output_text = tk.Text(window, height=10, width=80)
    output_text.pack(fill=tk.BOTH, expand=True)  # Adjust container size based on text

    window.mainloop()

if __name__ == '__main__':
    gui_interface()

