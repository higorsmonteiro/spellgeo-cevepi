'''
    For now, just save the schema

    After, we need to figure out how do we handle databases in the project (probably reflections)

    This file might be the initializer!
'''
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy import select, insert, update, text
from sqlalchemy import Table, MetaData
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Sequence, ForeignKey

class Schemas:
    def __init__(self, engine_path) -> None:
        self.engine_path = engine_path

    def define(self):
        '''
        
        '''
        # --> Initialize metadata
        metadata = MetaData()

        # --> Define schema of tables
        geonames = Table(
            'geonames', metadata,
            Column("ID_UNICO", String, Sequence('ID_UNICO', start=100), primary_key=True),
            Column("QUERY", String, nullable=False),
            Column("NUMERO_PAGINA", Integer),
            Column("LOGRADOURO/NOME", String),
            Column("BAIRRO/DISTRITO", String),
            Column("LOCALIDADE/UF", String),
            Column("CEP", String),
            Column('CRIADO_EM', DateTime, default=datetime.now)
        )

        geonames_log = Table(
            'geonames_log', metadata,
            Column("QUERY", String, nullable=False),
            Column("MENSAGEM", String, nullable=False),
            Column('CRIADO_EM', DateTime, default=datetime.now)
        )