import json
import base64
from algosdk.v2client import algod
from algosdk.future.transaction import AssetTransferTxn

from variables import purestake_token, my_wallet, my_wallet_pk, my_token_id


algod_address = "https://testnet-algorand.api.purestake.io/ps2"
headers = {"X-Api-key": purestake_token}
algod_client = algod.AlgodClient(algod_token=purestake_token, algod_address=algod_address, headers=headers)


def do_transaction(my_wallet, my_wallet_pk, dest_adress, amount, my_token_id):

    # build transaction with suggested params
    params = algod_client.suggested_params()
    note = "Rewards".encode()  # the note will be seen by the receiver in the txn

    # construct txn
    unsigned_txn = AssetTransferTxn(
        sender=my_wallet,
        sp=params,
        receiver=dest_adress,
        index=my_token_id,
        amt=amount,
        note=note
    )

    # sign transaction
    signed_txn = unsigned_txn.sign(my_wallet_pk)

    # submit transaction
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))

    # wait for confirmation
    try:
        confirmed_txn = wait_for_confirmation(algod_client, txid)
    except Exception as err:
        print(err)
        return

    print("Transaction information: {}".format(
        json.dumps(confirmed_txn, indent=4)))
    print("Decoded note: {}".format(base64.b64decode(
        confirmed_txn["txn"]["txn"]["note"]).decode()))


# Function from Algorand Inc. - utility for waiting on a transaction confirmation
def wait_for_confirmation(client, txid):
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print('Waiting for confirmation')
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print('Transaction confirmed in round', txinfo.get('confirmed-round'))
    return txinfo


def pay_battery(df_txs):

    for index, row in df_txs.iterrows():
        # token value to pay must be int; otherwise, txn will fail
        tokens_to_pay = row["tokens_to_pay"].astype(int).item()
        print("Starting transaction of {} to {}".format(tokens_to_pay, index))
        do_transaction(my_wallet, my_wallet_pk, index, tokens_to_pay, my_token_id)
