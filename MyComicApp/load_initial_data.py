import os
from django.db import connection
from django.conf import settings
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def load_data_script(sender, **kwargs):
    sql_file_path = os.path.join(settings.BASE_DIR, 'MyComicApp', 'initial_data.sql')

    if not os.path.exists(sql_file_path):
        print(f'SQL file not found: {sql_file_path}')
        return

    # Lista de tablas afectadas por el script
    affected_tables = ['categories', 'products', 'roles', 'mycomicapp_user', 'orders', 'order_items']

    # Verificar y cargar datos en cada tabla individualmente
    with connection.cursor() as cursor:
        for table in affected_tables:
            try:
                # Vaciar la tabla antes de cargar los datos
                cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
                print(f'Table {table} truncated')

                # Leer datos específicos para la tabla
                with open(sql_file_path, 'r') as file:
                    sql = file.read()
                    # Extraer solo los datos relevantes para la tabla actual
                    table_data = extract_table_data(sql, table)
                    if table_data:
                        cursor.execute(table_data)
                        print(f'Successfully loaded data for table {table}')
            except Exception as e:
                print(f"Skipping table {table} due to error: {e}")
                continue

def extract_table_data(sql, table):
    """
    Función auxiliar para extraer los datos de la tabla específica desde el archivo SQL.
    """
    # Dividir el SQL en sentencias individuales
    sql_statements = sql.split(';')
    table_data = []

    for statement in sql_statements:
        # Ignorar comentarios y sentencias vacías
        statement = statement.strip()
        if not statement or statement.startswith('--'):
            continue
        # Agregar las sentencias que contienen el nombre de la tabla
        if table in statement:
            table_data.append(statement)

    return ';\n'.join(table_data) + ';' if table_data else None
