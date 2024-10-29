from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Cache para armazenar o DataFrame
df_cache = None

def ler_planilha():
    """Lê a planilha Excel e retorna os dados"""
    try:
        global df_cache
        if df_cache is not None:
            return df_cache
        
        # Lê o arquivo Excel
        df = pd.read_excel('Base Clientes.xlsx')
        
        # Renomeia as colunas para corresponder aos nomes esperados
        df.columns = [
            'id',  # ID do cliente
            'nome',  # Nome
            'email',  # Email
            'telefone',  # Telefone
            'endereco',  # Endereço
            'cidade_estado',  # Cidade/Estado
            'ultima_compra',  # Última Compra
            'valor_total'  # Valor Total
        ]
        
        # Converte a coluna ID para número e remove possíveis espaços
        df['id'] = pd.to_numeric(df['id'].astype(str).str.strip(), errors='coerce')
        
        # Armazena no cache
        df_cache = df
        return df
    except Exception as e:
        print(f"Erro ao ler planilha: {e}")
        return None

@app.route('/api/cliente/<id>', methods=['GET'])
def buscar_cliente(id):
    """Busca um cliente pelo ID na planilha"""
    try:
        df = ler_planilha()
        if df is None:
            return jsonify({"erro": "Erro ao ler planilha"}), 500

        # Converte ID para número e busca o cliente
        id_cliente = int(id)
        cliente = df[df['id'] == id_cliente]

        if cliente.empty:
            return jsonify({"erro": "Cliente não encontrado"}), 404

        # Pega o primeiro resultado encontrado
        cliente = cliente.iloc[0]
        
        # Cria o dicionário com os dados do cliente
        cliente_dict = {
            "id": str(cliente['id']),
            "nome": str(cliente['nome']),
            "email": str(cliente['email']),
            "telefone": str(cliente['telefone']),
            "endereco": str(cliente['endereco']),
            "cidade": str(cliente['cidade_estado']).split('/')[0] if '/' in str(cliente['cidade_estado']) else str(cliente['cidade_estado']),
            "estado": str(cliente['cidade_estado']).split('/')[-1] if '/' in str(cliente['cidade_estado']) else "",
            "ultimaCompra": str(cliente['ultima_compra']),
            "valorTotal": str(cliente['valor_total'])
        }

        return jsonify(cliente_dict)

    except ValueError:
        return jsonify({"erro": "ID inválido"}), 400
    except Exception as e:
        print(f"Erro ao buscar cliente: {e}")
        return jsonify({"erro": f"Erro ao buscar cliente: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)