import psycopg2
from psycopg2 import sql
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, LOGGER

def create_database():
    """Create the database if it does not exist."""
    try:
        # Connect to PostgreSQL server without specifying a database
        conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        conn.autocommit = True  # Disables the transaction to execute CREATE DATABASE
        cursor = conn.cursor()
        
        # Check if the database already exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            LOGGER.info(f"✅ Base de datos '{DB_NAME}' creada correctamente.")
        else:
            LOGGER.info(f"⚠️ La base de datos '{DB_NAME}' ya existe.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        LOGGER.error(f"❌ Error al crear la base de datos: {e.pgcode} - {e.pgerror}")

def get_connection():
    """Returns a connection to PostgreSQL."""
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

def init_db():
    """Create the table if it does not exist."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS music_cache (
                        url TEXT PRIMARY KEY,
                        file_ids TEXT,
                        nombre TEXT,
                        artista TEXT,
                        album TEXT,
                        fecha TEXT,
                        imagen_url TEXT,
                        UNIQUE(nombre, artista, album)
                    )
                """)
                conn.commit()
                LOGGER.info("✅ Tabla 'music_cache' creada correctamente.")
    except psycopg2.Error as e:
        LOGGER.error(f"❌ Error al crear la tabla: {e.pgcode} - {e.pgerror}")


def save_to_db(url, file_ids, nombre, artista, album, fecha, imagen_url):
    """Saves or updates the information in the database."""
    if not file_ids:
        LOGGER.warning("⚠️ Lista de file_ids vacía, no se guardará en la base de datos")
        return
    
    file_ids_str = ",".join(file_ids)

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO music_cache (url, file_ids, nombre, artista, album, fecha, imagen_url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (url) DO UPDATE 
                    SET file_ids = EXCLUDED.file_ids, 
                        nombre = EXCLUDED.nombre, 
                        artista = EXCLUDED.artista, 
                        album = EXCLUDED.album, 
                        fecha = EXCLUDED.fecha, 
                        imagen_url = EXCLUDED.imagen_url;
                """, (url, file_ids_str, nombre, artista, album, fecha, imagen_url))
                conn.commit()
                LOGGER.info("✅ Datos guardados o actualizados en la base de datos.")
    except psycopg2.Error as e:
        LOGGER.error(f"❌ Error al guardar en la base de datos: {e.pgcode} - {e.pgerror}")

def get_from_db(url):
    """Gets the information associated with a URL from the database."""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT file_ids, nombre, artista, album, fecha, imagen_url FROM music_cache WHERE url = %s", (url,))
                row = cursor.fetchone()
                if row:
                    LOGGER.info(f"✅ Información obtenida de la base de datos para la URL: {url}")
                else:
                    LOGGER.info(f"⚠️ No se encontró información en la base de datos para la URL: {url}")
                return row
    except psycopg2.Error as e:
        LOGGER.error(f"❌ Error al consultar la URL {url} en la base de datos: {e.pgcode} - {e.pgerror}")
    return None  # Returns None in case of error