"""
[AGENTE_DATA_ENGINEER] — Qlik / CSV / XLSX Parser Service.

Core ETL service that:
  1. Detects file type and reads into a Pandas DataFrame
  2. Auto-classifies columns as categorical or numeric
  3. Generates Chart.js-ready JSON (labels + datasets)
  4. Memory-safe: limits output to aggregated summaries

Supports: .csv, .xlsx, .qvd (Qlik native)
"""
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Maximum rows to process before aggregating
MAX_RAW_ROWS = 50_000
# Maximum rows to return to frontend
MAX_DISPLAY_ROWS = 100

# Color palette for Chart.js datasets
CHART_COLORS = [
    'rgba(99, 102, 241, 0.8)',    # Indigo
    'rgba(16, 185, 129, 0.8)',    # Emerald
    'rgba(245, 158, 11, 0.8)',    # Amber
    'rgba(239, 68, 68, 0.8)',     # Red
    'rgba(139, 92, 246, 0.8)',    # Violet
    'rgba(6, 182, 212, 0.8)',     # Cyan
    'rgba(236, 72, 153, 0.8)',    # Pink
    'rgba(34, 197, 94, 0.8)',     # Green
    'rgba(251, 146, 60, 0.8)',    # Orange
    'rgba(59, 130, 246, 0.8)',    # Blue
]

CHART_BORDERS = [c.replace('0.8', '1') for c in CHART_COLORS]


def read_file_to_dataframe(filepath):
    """
    Read a data file into a Pandas DataFrame.
    Supports: .csv, .xlsx, .qvd
    """
    path = Path(filepath)
    ext = path.suffix.lower()

    logger.info(f'[DATA_ENGINEER] Reading file: {path.name} ({ext})')

    if ext == '.csv':
        # Try different encodings and delimiters
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            for sep in [',', ';', '\t', '|']:
                try:
                    df = pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=5)
                    if len(df.columns) > 1:
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=MAX_RAW_ROWS)
                        logger.info(f'[DATA_ENGINEER] CSV parsed: {len(df)} rows, encoding={encoding}, sep=repr({sep})')
                        return df
                except Exception:
                    continue
        # Fallback: basic read
        df = pd.read_csv(filepath, nrows=MAX_RAW_ROWS)
        return df

    elif ext in ('.xlsx', '.xls'):
        df = pd.read_excel(filepath, nrows=MAX_RAW_ROWS)
        logger.info(f'[DATA_ENGINEER] Excel parsed: {len(df)} rows')
        return df

    elif ext == '.qvd':
        try:
            from qvd import qvd_reader
            df = qvd_reader.read(str(filepath))
            if len(df) > MAX_RAW_ROWS:
                logger.warning(f'[DATA_ENGINEER] QVD too large ({len(df)} rows), truncating to {MAX_RAW_ROWS}')
                df = df.head(MAX_RAW_ROWS)
            logger.info(f'[DATA_ENGINEER] QVD parsed: {len(df)} rows')
            return df
        except ImportError:
            raise ImportError(
                'Librería "qvd" no instalada. Ejecuta: pip install qvd'
            )

    else:
        raise ValueError(f'Formato de archivo no soportado: "{ext}"')


def classify_columns(df):
    """
    Auto-classify DataFrame columns into categorical and numeric.
    Returns { 'categorical': [...], 'numeric': [...], 'datetime': [...], 'all': [...] }
    """
    categorical = []
    numeric = []
    datetime_cols = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric.append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            datetime_cols.append(col)
        else:
            # Try to parse as datetime
            try:
                pd.to_datetime(df[col].dropna().head(10))
                datetime_cols.append(col)
            except (ValueError, TypeError):
                categorical.append(col)

    return {
        'categorical': categorical,
        'numeric': numeric,
        'datetime': datetime_cols,
        'all': [
            {'name': c, 'type': 'numeric' if c in numeric else 'datetime' if c in datetime_cols else 'categorical'}
            for c in df.columns
        ],
    }


def generate_chart_data(df, columns_info):
    """
    Generate Chart.js-ready JSON from a DataFrame.
    Returns multiple chart configurations:
      - summary: basic stats
      - bar_charts: top categorical columns grouped by numeric
      - pie_charts: value distribution of categorical columns
      - table_preview: first N rows
    """
    charts = []
    cat_cols = columns_info['categorical']
    num_cols = columns_info['numeric']

    # ── Bar Charts: categorical × numeric aggregations ──
    for cat_col in cat_cols[:3]:  # Max 3 categorical columns
        for num_col in num_cols[:3]:  # Max 3 numeric per category
            try:
                grouped = df.groupby(cat_col)[num_col].sum().nlargest(15)
                if grouped.empty:
                    continue

                labels = [str(l) for l in grouped.index.tolist()]
                values = [round(float(v), 2) if pd.notna(v) else 0 for v in grouped.values]

                charts.append({
                    'id': f'bar_{cat_col}_{num_col}',
                    'type': 'bar',
                    'title': f'{num_col} por {cat_col}',
                    'data': {
                        'labels': labels,
                        'datasets': [{
                            'label': num_col,
                            'data': values,
                            'backgroundColor': CHART_COLORS[:len(values)],
                            'borderColor': CHART_BORDERS[:len(values)],
                            'borderWidth': 1,
                        }],
                    },
                })
            except Exception as e:
                logger.warning(f'[DATA_ENGINEER] Error generating bar chart for {cat_col}/{num_col}: {e}')

    # ── Pie/Doughnut Charts: categorical value distribution ──
    for cat_col in cat_cols[:2]:  # Max 2 pie charts
        try:
            counts = df[cat_col].value_counts().nlargest(10)
            if counts.empty:
                continue

            labels = [str(l) for l in counts.index.tolist()]
            values = [int(v) for v in counts.values]

            charts.append({
                'id': f'pie_{cat_col}',
                'type': 'doughnut',
                'title': f'Distribución: {cat_col}',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': CHART_COLORS[:len(values)],
                        'borderColor': 'rgba(15, 23, 42, 1)',
                        'borderWidth': 2,
                    }],
                },
            })
        except Exception as e:
            logger.warning(f'[DATA_ENGINEER] Error generating pie chart for {cat_col}: {e}')

    # ── Line Charts: numeric trends (if datetime present) ──
    dt_cols = columns_info['datetime']
    if dt_cols and num_cols:
        dt_col = dt_cols[0]
        try:
            df_copy = df.copy()
            df_copy[dt_col] = pd.to_datetime(df_copy[dt_col], errors='coerce')
            df_copy = df_copy.dropna(subset=[dt_col]).sort_values(dt_col)

            if len(df_copy) > MAX_DISPLAY_ROWS:
                # Resample by grouping
                df_copy = df_copy.set_index(dt_col)
                freq = 'ME' if len(df_copy) > 365 else 'W' if len(df_copy) > 60 else 'D'
                df_copy = df_copy[num_cols[:2]].resample(freq).sum().reset_index()

            labels = [d.strftime('%Y-%m-%d') for d in df_copy[dt_col]]
            datasets = []
            for i, num_col in enumerate(num_cols[:2]):
                datasets.append({
                    'label': num_col,
                    'data': [round(float(v), 2) if pd.notna(v) else 0 for v in df_copy[num_col]],
                    'borderColor': CHART_COLORS[i],
                    'backgroundColor': CHART_COLORS[i].replace('0.8', '0.1'),
                    'tension': 0.3,
                    'fill': True,
                })

            charts.append({
                'id': f'line_{dt_col}',
                'type': 'line',
                'title': f'Tendencia temporal: {dt_col}',
                'data': {
                    'labels': labels,
                    'datasets': datasets,
                },
            })
        except Exception as e:
            logger.warning(f'[DATA_ENGINEER] Error generating line chart: {e}')

    return charts


def generate_summary(df):
    """Generate statistical summary of the DataFrame."""
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        'numeric_stats': {},
    }

    for col in df.select_dtypes(include='number').columns[:5]:
        try:
            summary['numeric_stats'][col] = {
                'mean': round(float(df[col].mean()), 2) if pd.notna(df[col].mean()) else None,
                'sum': round(float(df[col].sum()), 2),
                'min': round(float(df[col].min()), 2) if pd.notna(df[col].min()) else None,
                'max': round(float(df[col].max()), 2) if pd.notna(df[col].max()) else None,
            }
        except Exception:
            pass

    return summary


def generate_table_preview(df, max_rows=50):
    """Generate a table preview (first N rows) for the frontend."""
    preview_df = df.head(max_rows)
    columns = list(preview_df.columns)

    rows = []
    for _, row in preview_df.iterrows():
        rows.append({
            col: (str(v) if pd.notna(v) else None)
            for col, v in row.items()
        })

    return {
        'columns': columns,
        'rows': rows,
        'total_rows': len(df),
        'showing': len(rows),
    }


def process_file(filepath):
    """
    Full ETL pipeline: read → classify → generate charts + summary + preview.
    Returns a complete JSON structure ready for the frontend.
    """
    df = read_file_to_dataframe(filepath)
    columns_info = classify_columns(df)
    charts = generate_chart_data(df, columns_info)
    summary = generate_summary(df)
    table_preview = generate_table_preview(df)

    return {
        'summary': summary,
        'columns': columns_info['all'],
        'charts': charts,
        'table_preview': table_preview,
    }, len(df), len(df.columns), columns_info['all']
