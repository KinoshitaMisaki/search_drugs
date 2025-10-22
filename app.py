from flask import Flask, render_template, request, jsonify
import polars as pl
import os
from io import BytesIO
import glob
import datetime
import math

app = Flask(__name__)
ITEMS_PER_PAGE = 50

# Load data
def load_data():
    csv_files = glob.glob('csvs/*.csv')
    xlsx_files = glob.glob('csvs/*.xlsx')
    if not csv_files:
        return pl.DataFrame()

    columns = ['薬品名(和名)', '薬品名(英名)', 'メーカー名', '型番']
    # Define dtypes to prevent schema errors
    dtypes = {'JANコード': pl.Utf8, '型番': pl.Utf8}

    df1 = pl.concat([
        pl.read_csv(file, infer_schema_length=100000, dtypes=dtypes).select(columns)
        for file in csv_files
    ])

    df2 = pl.concat([
    pl.read_excel(file,sheet_name="Chemical",
                    read_csv_options={"infer_schema_length": 100000, "skip_rows":0, "ignore_errors":True, "has_header":True}).slice(2,None).select(columns)
    for file in xlsx_files
    ])
    
    df = pl.concat([df1, df2])

    return df

data = load_data()

def filter_data(product_name, manufacturer, model_number):
    """Filters the dataframe based on search criteria in a case-insensitive manner."""
    filtered_df = data
    if product_name:
        product_name_lower = product_name.lower()
        filtered_df = filtered_df.filter(
            pl.col('薬品名(和名)').str.to_lowercase().str.contains(product_name_lower, literal=False) |
            pl.col('薬品名(英名)').str.to_lowercase().str.contains(product_name_lower, literal=False)
        )
    if manufacturer:
        manufacturer_lower = manufacturer.lower()
        filtered_df = filtered_df.filter(
            pl.col('メーカー名').str.to_lowercase().str.contains(manufacturer_lower, literal=False)
        )
    if model_number:
        model_number_lower = model_number.lower()
        filtered_df = filtered_df.filter(
            pl.col('型番').str.to_lowercase().str.contains(model_number_lower, literal=False)
        )
    return filtered_df


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    offset = (page - 1) * ITEMS_PER_PAGE

    total_items = len(data)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)

    paginated_data = data.slice(offset, ITEMS_PER_PAGE).to_dicts()

    return render_template(
        'index.html',
        results=paginated_data,
        total_pages=total_pages,
        current_page=page,
        total_items=total_items
    )

@app.route('/search')
def search():
    page = request.args.get('page', 1, type=int)
    product_name = request.args.get('product_name', '')
    manufacturer = request.args.get('manufacturer', '')
    model_number = request.args.get('model_number', '')

    filtered_df = filter_data(product_name, manufacturer, model_number)

    total_items = len(filtered_df)
    total_pages = math.ceil(total_items / ITEMS_PER_PAGE)

    offset = (page - 1) * ITEMS_PER_PAGE
    paginated_data = filtered_df.slice(offset, ITEMS_PER_PAGE).to_dicts()

    return jsonify({
        'results': paginated_data,
        'total_pages': total_pages,
        'current_page': page,
        'total_items': total_items
    })


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
