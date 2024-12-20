from flask import Blueprint, request, jsonify, abort
from app.core.use_cases.process_payment import ProcessPayment
from app.infrastructure.web.payment_service import PaymentService
import requests

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pagamento/<id_pedido>', methods=['POST'])
def efetuar_pagamento(id_pedido):
    status_pagamento = PaymentService().process_payment(id_pedido)

    # Dados para o webhook
    webhook_data = {
        "idPedido": id_pedido,
        "status": status_pagamento
    }

    # URL do webhook
    webhook_url = 'http://k8s-default-ingressa-0faf251d7e-1124737897.sa-east-1.elb.amazonaws.com/avalanches/v1/pagamento/webhook'
    
    # Enviar requisição POST para o webhook
    try:
        response = requests.post(webhook_url, json=webhook_data, headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Levanta um erro para códigos de status 4xx/5xx
        print(f"Webhook acionado com sucesso: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acionar o webhook: {e}")
  
    if status_pagamento != "APROVADO":
        abort(400, description=f"Pagamento não aprovado para o pedido {id_pedido}. Status: {status_pagamento}")

    return jsonify({"id_pedido": id_pedido, "status": status_pagamento})
