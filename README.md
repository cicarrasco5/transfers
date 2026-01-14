# Transfers

Este proyecto permite realizar transferencias automáticas de cualquier monto utilizando la API de Fintoc.

## Requisitos

1. Python 3.7 o superior
2. Instalar dependencias:
	 ```bash
	 pip install -r requirements.txt
	 ```

## Configuración

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```
API_KEY=tu_api_key_de_fintoc
JWS_PRIVATE_KEY_PATH=private_key.pem
MAX_TRANSFER_AMOUNT=7000000
MAX_RETRIES=3
```

Se debe tener el archivo `private_key.pem` en el directorio del proyecto.

## Uso

Argumentos requeridos:
- `--account_id`: ID de la cuenta origen        
- `--amount`: Monto total a transferir
- `--currency`: Moneda de la transferencia
- `--counterparty_account_number`: Número de cuenta destino
- `--counterparty_institution_id`: ID de la institución destino
- `--counterparty_holder_id`: ID del titular destino
- `--counterparty_account_type`: Tipo de cuenta destino

Argumentos opcionales:
- `--counterparty_holder_name`: Nombre del titular destino
- `--metadata_client_id`: ID de cliente para metadata
- `--comment`: Comentario personalizado para la transferencia

El script dividirá el monto total en transferencias según el máximo configurado y reintentará cada transferencia hasta el máximo de reintentos definido por `MAX_RETRIES`.