import argparse, os, math, logging, datetime
from dotenv import load_dotenv
from fintoc import Fintoc

logging.basicConfig(filename='transfers.log',level=logging.INFO)

def parse_args():
    parser = argparse.ArgumentParser(description="Fintoc Transfers Script")
    parser.add_argument("--account_id", type=str, required=True, help="Account ID to transfer from")
    parser.add_argument("--amount", type=int, required=True, help="Total amount to transfer")
    parser.add_argument("--currency", type=str, required=True, help="Currency of the transfer")
    parser.add_argument("--counterparty_account_number", type=str, required=True, help="Counterparty account number")
    parser.add_argument("--counterparty_institution_id", type=str, required=True, help="Counterparty institution ID")
    parser.add_argument("--counterparty_holder_id", type=str, required=True, help="Counterparty holder ID")
    parser.add_argument("--counterparty_account_type", type=str, required=True, help="Counterparty account type")
    parser.add_argument("--counterparty_holder_name", type=str, required=False, help="Counterparty holder name")
    parser.add_argument("--metadata_client_id", type=str, required=False, help="Metadata client ID")
    parser.add_argument("--comment", type=str, required=False, help="Comment for the transfer")

    return parser.parse_args()

def main():
    for var in ["API_KEY", "JWS_PRIVATE_KEY_PATH"]:
        if not os.getenv(var):
            raise EnvironmentError(f"Missing environment variable: {var}")
    api_key = os.getenv("API_KEY")
    jws_private_key_path = os.getenv("JWS_PRIVATE_KEY_PATH")
    max_transfer_amount = int(os.getenv("MAX_TRANSFER_AMOUNT", "7000000"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))

    if args.amount <= 0:
        raise ValueError("Amount must be greater than 0")

    client = Fintoc(api_key, jws_private_key=jws_private_key_path)

    transfers = {}
    total_amount = args.amount
    transfer_count = 1
    retries = 0

    counterparty = {
        "account_number": args.counterparty_account_number,
        "institution_id": args.counterparty_institution_id,
        "holder_id": args.counterparty_holder_id,
        "account_type": args.counterparty_account_type}
    if args.counterparty_holder_name:
        counterparty["holder_name"] = args.counterparty_holder_name
    metadata = {}
    if args.metadata_client_id:
        metadata["client_id"] = args.metadata_client_id
        
    while total_amount > 0 and retries < max_retries:
        transfer_amount = min(total_amount, max_transfer_amount)
        print(f"Initiating transfer {transfer_count}: {transfer_amount} {args.currency}")
        try:
            transfer = client.v2.transfers._create(
                url="https://api.fintoc.com/v2/transfers",
                account_id=args.account_id,
                amount=transfer_amount,
                currency=args.currency,
                comment=f"{args.comment if args.comment else 'Automated Transfer'} {transfer_count}/{math.ceil(args.amount / max_transfer_amount)}",
                counterparty=counterparty,
                metadata=metadata
            )
            total_amount -= transfer_amount
            transfer_count += 1
            transfers[transfer.id] = transfer
        except Exception as e:
            logging.error(f"Error during transfer: {e}")
            retries += 1
            print("An error occurred. Check transfers.log for details.")
            continue

    for t_id in transfers.keys():
        try:
            t = client.v2.transfers.get(t_id)
            transfers[t_id] = t
        except Exception as e:
            transfers[t_id]['status'] = 'error'
            logging.error(f"Error fetching transfer {t_id}: {e}")

    with open('transfers_report.csv', 'w') as f:
        f.write("id,status,amount,currency,transaction_date,post_date,comment\n")
        for t in transfers.values():
            created_at = datetime.datetime.fromtimestamp(t.created_at).isoformat() if hasattr(t, 'transaction_date') else ''
            completed_at = datetime.datetime.fromtimestamp(t.completed_at).isoformat() if hasattr(t, 'post_date') else ''
            comment = getattr(t, 'comment', '')
            f.write(f"{t.id},{getattr(t, 'status', '')},{getattr(t, 'amount', '')},{getattr(t, 'currency', '')},{created_at},{completed_at},{comment}\n")

if __name__ == "__main__":
    load_dotenv()
    args = parse_args()
    main()