"""
[AGENTE_DATA_ENGINEER] — QlikEngine: Data Manager & ETL.

Provides:
  - extract_metadata(): Read file → column names, types, row count, preview
  - execute_load_script(): Read DataModelConfig JSON → load, join, return records
"""
import logging
from pathlib import Path

import pandas as pd

from reports.models import DataSource

logger = logging.getLogger(__name__)

MAX_PREVIEW_ROWS = 50
MAX_LOAD_ROWS = 100_000


class QlikEngine:
    """In-memory ETL engine that reads files and executes load scripts."""

    @staticmethod
    def _read_file(filepath):
        """Read a data file into a Pandas DataFrame."""
        path = Path(filepath)
        ext = path.suffix.lower()

        if ext == '.csv':
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                for sep in [',', ';', '\t', '|']:
                    try:
                        df = pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=5)
                        if len(df.columns) > 1:
                            return pd.read_csv(filepath, encoding=encoding, sep=sep, nrows=MAX_LOAD_ROWS)
                    except Exception:
                        continue
            return pd.read_csv(filepath, nrows=MAX_LOAD_ROWS)

        elif ext in ('.xlsx', '.xls'):
            return pd.read_excel(filepath, nrows=MAX_LOAD_ROWS)

        elif ext == '.qvd':
            try:
                from qvd import qvd_reader
                df = qvd_reader.read(str(filepath))
                return df.head(MAX_LOAD_ROWS) if len(df) > MAX_LOAD_ROWS else df
            except ImportError:
                raise ImportError('Librería "qvd" no instalada.')

        raise ValueError(f'Formato no soportado: {ext}')

    @staticmethod
    def extract_metadata(datasource):
        """
        Read a DataSource file and extract metadata.
        Returns dict with columns info, row count, and preview rows.
        """
        df = QlikEngine._read_file(datasource.file.path)

        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            if pd.api.types.is_numeric_dtype(df[col]):
                col_type = 'numeric'
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                col_type = 'datetime'
            else:
                col_type = 'categorical'

            columns.append({
                'name': col,
                'type': col_type,
                'dtype': dtype,
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique()),
            })

        # Preview: first N rows as list of dicts
        preview_df = df.head(MAX_PREVIEW_ROWS)
        preview = []
        for _, row in preview_df.iterrows():
            preview.append({
                col: (str(v) if pd.notna(v) else None)
                for col, v in row.items()
            })

        return {
            'columns': columns,
            'row_count': len(df),
            'column_count': len(df.columns),
            'preview': preview,
        }

    @staticmethod
    def execute_load_script(data_model_config):
        """
        Execute a DataModelConfig's load_script_json.

        Schema expected:
        {
            "sources": [
                {"source_id": 1, "columns": ["Col1", "Col2"]},
                {"source_id": 2, "columns": ["ID", "Name"]}
            ],
            "joins": [
                {
                    "left_source": 1,
                    "right_source": 2,
                    "left_key": "CodCliente",
                    "right_key": "ID",
                    "how": "left"
                }
            ]
        }

        Returns: dict with columns, rows (records), and row_count.
        """
        script = data_model_config.load_script_json
        sources_config = script.get('sources', [])
        joins_config = script.get('joins', [])

        if not sources_config:
            raise ValueError('El script de carga no tiene fuentes de datos configuradas.')

        # Load all source DataFrames
        dataframes = {}
        for src in sources_config:
            source_id = src['source_id']
            selected_columns = src.get('columns', [])

            try:
                ds = DataSource.objects.get(pk=source_id)
            except DataSource.DoesNotExist:
                raise ValueError(f'Fuente de datos ID={source_id} no existe.')

            df = QlikEngine._read_file(ds.file.path)

            # Filter columns if specified
            if selected_columns:
                available = [c for c in selected_columns if c in df.columns]
                if available:
                    df = df[available]

            dataframes[source_id] = df
            logger.info(f'[QLIK_ENGINE] Loaded source {source_id}: {len(df)} rows × {len(df.columns)} cols')

        # Execute joins sequentially
        if joins_config:
            # Start with first join's left source
            first_join = joins_config[0]
            result_df = dataframes.get(first_join['left_source'])
            if result_df is None:
                raise ValueError(f'Fuente izquierda {first_join["left_source"]} no encontrada.')

            for join in joins_config:
                right_df = dataframes.get(join['right_source'])
                if right_df is None:
                    raise ValueError(f'Fuente derecha {join["right_source"]} no encontrada.')

                how = join.get('how', 'left')
                if how not in ('left', 'right', 'inner', 'outer'):
                    how = 'left'

                result_df = pd.merge(
                    result_df,
                    right_df,
                    left_on=join['left_key'],
                    right_on=join['right_key'],
                    how=how,
                    suffixes=('', f'_{join["right_source"]}'),
                )
                logger.info(
                    f'[QLIK_ENGINE] Join: {join["left_key"]} ↔ {join["right_key"]} '
                    f'({how}) → {len(result_df)} rows'
                )
        else:
            # No joins — use the first (or only) source
            first_id = sources_config[0]['source_id']
            result_df = dataframes[first_id]

        # Build response
        columns = list(result_df.columns)
        records = []
        for _, row in result_df.head(MAX_PREVIEW_ROWS * 2).iterrows():
            records.append({
                col: (float(v) if pd.api.types.is_numeric_dtype(type(v)) and pd.notna(v)
                      else str(v) if pd.notna(v) else None)
                for col, v in row.items()
            })

        # Column classification for chart building
        col_info = []
        for col in columns:
            if pd.api.types.is_numeric_dtype(result_df[col]):
                col_info.append({'name': col, 'type': 'numeric'})
            else:
                col_info.append({'name': col, 'type': 'categorical'})

        return {
            'columns': col_info,
            'rows': records,
            'row_count': len(result_df),
            'showing': len(records),
        }
