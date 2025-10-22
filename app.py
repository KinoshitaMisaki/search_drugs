from flask import Flask, render_template, request, jsonify
import polars as pl
import os
from io import BytesIO
import glob
import datetime

app = Flask(__name__)

# Load data
def load_data():
    csv_files = glob.glob('csvs/*.csv')
    if not csv_files:
        return pl.DataFrame()

    columns = ['薬品名(和名)', '薬品名(英名)', 'JANコード', 'メーカー名', '型番']
    # Define dtypes to prevent schema errors
    schema = {'JANコード': pl.Utf8, '型番': pl.Utf8}

    df = pl.concat([
        pl.read_csv(file, infer_schema_length=500000, dtypes=schema).select(columns)
        for file in csv_files
    ])
    return df

data = load_data()

def filter_data(product_name, manufacturer, model_number):
    """Filters the dataframe based on search criteria."""
    filtered_df = data
    if product_name:
        filtered_df = filtered_df.filter(
            pl.col('薬品名(和名)').str.contains(product_name, literal=False) |
            pl.col('薬品名(英名)').str.contains(product_name, literal=False)
        )
    if manufacturer:
        filtered_df = filtered_df.filter(pl.col('メーカー名').str.contains(manufacturer, literal=False))
    if model_number:
        filtered_df = filtered_df.filter(pl.col('型番').str.contains(model_number, literal=False))
    return filtered_df


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    product_name = request.args.get('product_name', '')
    manufacturer = request.args.get('manufacturer', '')
    model_number = request.args.get('model_number', '')

    filtered_df = filter_data(product_name, manufacturer, model_number)
    return jsonify(filtered_df.to_dicts())

@app.route('/export_csv')
def export_csv():
    product_name = request.args.get('product_name', '')
    manufacturer = request.args.get('manufacturer', '')
    model_number = request.args.get('model_number', '')

    filtered_df = filter_data(product_name, manufacturer, model_number)

    # Select only the required columns for export
    export_columns = ['薬品名(和名)', '薬品名(英名)', '型番', 'メーカー名']
    export_df = filtered_df.select(export_columns)

    # Create CSV in memory
    buffer = BytesIO()
    # Write BOM for UTF-8
    buffer.write(b'\xef\xbb\xbf')
    export_df.write_csv(buffer)
    buffer.seek(0)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    return app.response_class(
        buffer.getvalue(),
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment;filename=export_{timestamp}.csv"}
    )


if __name__ == '__main__':
    app.run(debug=True)
