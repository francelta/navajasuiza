"""
Klaes SQL Server Connection — ODBC via SQLAlchemy.
Connects to the external Klaes database on the local network (Windows).

[AGENTE_DEVOPS] Uses ODBC Driver 17 for SQL Server.
[AGENTE_SEGURIDAD] Connection string built from .env, never hardcoded.
"""
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from django.conf import settings

logger = logging.getLogger(__name__)

# Engine singleton — created once, reused across requests
_engine = None


def _get_engine():
    """Lazy-initialize the SQLAlchemy engine for Klaes SQL Server."""
    global _engine
    if _engine is None:
        conn_str = settings.KLAES_DB_CONNECTION_STRING
        if not conn_str:
            raise RuntimeError(
                'KLAES_DB_CONNECTION_STRING no está configurada. '
                'Revisa las variables KLAES_DB_* en el archivo .env.'
            )
        _engine = create_engine(conn_str, pool_pre_ping=True, pool_size=3)
        logger.info('Klaes SQL Server engine initialized.')
    return _engine


@contextmanager
def klaes_connection():
    """
    Context manager that yields a SQLAlchemy connection.
    Usage:
        with klaes_connection() as conn:
            result = conn.execute(text("SELECT ..."))
    """
    engine = _get_engine()
    conn = engine.connect()
    try:
        yield conn
        conn.commit()
    except SQLAlchemyError:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_material_info(material_id):
    """
    Query material data from the Klaes database.
    Returns a dict with material fields or None if not found.
    """
    query = text("""
        SELECT
            ArtNr           AS material_id,
            ArtBez1         AS descripcion,
            ArtBez2         AS descripcion2,
            ArtGruppe       AS grupo,
            Einheit         AS unidad,
            VKPreis         AS precio_venta,
            EKPreis         AS precio_compra,
            Lieferant       AS proveedor,
            LiefArtNr       AS ref_proveedor,
            Bemerkung       AS observaciones,
            Gesperrt        AS bloqueado
        FROM Artikel
        WHERE ArtNr = :material_id
    """)

    with klaes_connection() as conn:
        row = conn.execute(query, {'material_id': material_id}).mappings().first()

    if row is None:
        return None

    return dict(row)


def update_material_price(material_id, new_price, updated_by='API_NAVAJASUIZA'):
    """
    Update the sale price (VKPreis) for a material in the Klaes database.
    Logs the audit trail with updated_by user.
    Returns (success: bool, message: str).
    """
    # Verify material exists first
    check_query = text("SELECT ArtNr FROM Artikel WHERE ArtNr = :material_id")
    update_query = text("""
        UPDATE Artikel
        SET VKPreis = :new_price
        WHERE ArtNr = :material_id
    """)

    # Audit log — record who changed the price
    audit_query = text("""
        INSERT INTO ArtikelLog (ArtNr, Feld, AlterWert, NeuerWert, Benutzer, Datum)
        SELECT
            :material_id,
            'VKPreis',
            CAST(VKPreis AS NVARCHAR(50)),
            CAST(:new_price AS NVARCHAR(50)),
            :updated_by,
            GETDATE()
        FROM Artikel
        WHERE ArtNr = :material_id
    """)

    try:
        with klaes_connection() as conn:
            # Check existence
            exists = conn.execute(check_query, {'material_id': material_id}).first()
            if not exists:
                return False, f'Material "{material_id}" no encontrado en Klaes.'

            # Try audit log (non-fatal if table doesn't exist)
            try:
                conn.execute(audit_query, {
                    'material_id': material_id,
                    'new_price': new_price,
                    'updated_by': updated_by,
                })
            except SQLAlchemyError as e:
                logger.warning(f'Audit log failed (table may not exist): {e}')

            # Execute update
            result = conn.execute(update_query, {
                'material_id': material_id,
                'new_price': new_price,
            })

            if result.rowcount == 0:
                return False, 'No se actualizó ningún registro.'

            logger.info(
                f'[KLAES] Price updated: {material_id} → {new_price} '
                f'by {updated_by}'
            )
            return True, f'Precio de "{material_id}" actualizado a {new_price}.'

    except SQLAlchemyError as e:
        logger.error(f'[KLAES] SQL Error updating price: {e}')
        return False, f'Error de base de datos: {str(e)}'


def get_quotation_details(q_number):
    """
    Query quotation (presupuesto) from Klaes: header + line items.
    Exact SQL from FastAPI codebase, column names in German preserved.
    Returns (data_dict, None) on success or (None, error_message) on failure.
    """
    header_query = text("""
        SELECT
            p.ProjNr as ID,
            p.Status as EstadoInterno,
            p.DruckStatus as EstadoImpresion,
            p.DruckModus as ModalidadImpresion,
            a.Name1 as Cliente,
            p.Datum as Fecha,
            p.GesamtNetto as PrecioTotalNeto,
            p.Waehrung as Moneda
        FROM PR_Projekte p
        LEFT JOIN AD_Adressen a ON p.AdressID = a.AdressID
        WHERE p.ProjNr = :q_id
    """)

    items_query = text("""
        SELECT
            PosNr,
            Stueck as Cantidad,
            Bezeichnung as Descripcion,
            Breite as Ancho,
            Hoehe as Alto,
            EinzelPreis as PrecioUnitario
        FROM PO_Positionen
        WHERE ProjNr = :q_id
        ORDER BY PosNr ASC
    """)

    with klaes_connection() as conn:
        header = conn.execute(header_query, {'q_id': q_number}).mappings().first()

        if header is None:
            return None, f'El presupuesto "{q_number}" no existe.'

        items = conn.execute(items_query, {'q_id': q_number}).mappings().fetchall()

        return {
            'existe': True,
            'cabecera': dict(header),
            'items': [dict(row) for row in items],
            'total_items': len(items),
        }, None
