import os
from flask import Flask, request, render_template
import pandas as pd
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def extract_details_and_save():
    if request.method == 'POST':
        excel_file = request.files.get('file')
        name_to_filter = request.form.get('name')
        columns = request.form.get('columns')

        if not excel_file or not name_to_filter or not columns:
            return "Error: Missing required inputs."

        # Define the upload folder path
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)  # Create the folder if it doesn't exist

        # Save the file to the upload folder
        file_path = os.path.join(upload_folder, excel_file.filename)
        excel_file.save(file_path)

        # Load the Excel file into a pandas DataFrame
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
        except Exception as e:
            logging.error(f"Error reading the Excel file: {e}")
            return f"Error reading the Excel file: {e}"

        # Apply filtering if a name is provided
        if name_to_filter:
            df = df[df.apply(lambda row: row.astype(str).str.contains(name_to_filter, case=False).any(), axis=1)]

        # Convert column input into a list of column names
        try:
            columns_list = [col.strip() for col in columns.split(',')]
            filtered_df = df[columns_list]
        except KeyError as e:
            logging.error(f"Error: One or more specified columns do not exist. {e}")
            return f"Error: One or more specified columns do not exist. {e}"
        except Exception as e:
            logging.error(f"Error processing columns: {e}")
            return f"Error processing columns: {e}"

        # Save the filtered data to a new Excel file
        output_file_path = os.path.join(upload_folder, 'filtered_output.xlsx')
        try:
            filtered_df.to_excel(output_file_path, index=False)
            return f"Filtered data saved to {output_file_path}"
        except Exception as e:
            logging.error(f"Error saving the filtered data: {e}")
            return f"Error saving the filtered data: {e}"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
