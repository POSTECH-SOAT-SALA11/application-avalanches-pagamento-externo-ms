import os
import psycopg2
import redis


class PaymentRepository:
    def __init__(self):
        # Conexão com o PostgreSQL
        self.conn = psycopg2.connect(
            dbname=os.environ['POSTGRES_DATABASE'],
            user=os.environ['POSTGRES_USER'],
            password=os.environ['POSTGRES_PASSWORD'],
            host=os.environ['POSTGRES_HOST'],
            port=os.environ['POSTGRES_PORT']
        )

        # Conexão com o Redis
        self.redis_client = redis.Redis(
            host=os.environ['REDIS_HOST'],
            port=os.environ['REDIS_PORT'],
            db=0  # Usando o banco de dados 0 do Redis
        )

    def save_payment(self, id_pedido, status_pagamento):
        # Salvar no PostgreSQL
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO pagamento (id_pedido, status) VALUES (%s, %s) "
            "ON CONFLICT (id_pedido) DO UPDATE SET status = EXCLUDED.status",
            (id_pedido, status_pagamento)
        )
        self.conn.commit()
        cur.close()

        # Salvar no Redis
        self.save_payment_redis(id_pedido, status_pagamento)

        self.conn.close()

    def save_payment_redis(self, id_pedido, status_pagamento):
        # Vamos salvar os dados no Redis com a chave sendo o id do pedido
        payment_data = {
            'id_pedido': id_pedido,
            'status': status_pagamento
        }

        # Salvando como um hash no Redis (estrutura de dados ideal para chave-valor complexos)
        self.redis_client.hmset(f'payment:{id_pedido}', payment_data)

        # Configurar um TTL (tempo de vida) para o dado, se for necessário (por exemplo, 1 hora)
        self.redis_client.expire(f'payment:{id_pedido}', 3600)
