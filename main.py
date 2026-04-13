from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2

DATABASE_URL = "postgresql://neondb_owner:npg_lXCWb2uA5rzQ@ep-sparkling-union-acpg28mq-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def conectar_banco():
    return psycopg2.connect(DATABASE_URL)

def criar_tabela():
    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id SERIAL PRIMARY KEY,
            ip VARCHAR(50),
            tipo_cliente VARCHAR(10),
            valor_compra FLOAT,
            desconto FLOAT,
            cashback FLOAT,
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

criar_tabela()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def calcular_cashback(valor_compra, desconto, vip):
    valor_final = valor_compra - (valor_compra / 100 * desconto)
    cashback_base = valor_final / 100 * 5
    vip_desconto = 0

    if valor_final > 500:
        cashback_base = 2 * cashback_base
    if vip == True:
        vip_desconto = cashback_base / 100 * 10

    return cashback_base + vip_desconto

@app.get("/cashback")
def calcular(valor_compra: float, desconto: float, vip: bool, request: Request):
    cashback = calcular_cashback(valor_compra, desconto, vip)
    
    ip = request.client.host
    tipo_cliente = "VIP" if vip else "Comum"

    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO consultas (ip, tipo_cliente, valor_compra, desconto, cashback)
        VALUES (%s, %s, %s, %s, %s)
    """, (ip, tipo_cliente, valor_compra, desconto, cashback))
    conn.commit()
    cur.close()
    conn.close()

    return {"cashback": cashback}

@app.get("/historico")
def historico(request: Request):
    ip = request.client.host
    
    conn = conectar_banco()
    cur = conn.cursor()
    cur.execute("""
        SELECT tipo_cliente, valor_compra, desconto, cashback, data
        FROM consultas
        WHERE ip = %s
        ORDER BY data DESC
    """, (ip,))
    
    registros = cur.fetchall()
    cur.close()
    conn.close()
    
    return {"historico": [
        {
            "tipo_cliente": r[0],
            "valor_compra": r[1],
            "desconto": r[2],
            "cashback": r[3],
            "data": r[4]
        }
        for r in registros
    ]}