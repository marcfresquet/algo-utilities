import pandas as pd
from algosdk.v2client import indexer

from variables import purestake_token

headers = {
   "X-API-Key": purestake_token,
}
myindexer = indexer.IndexerClient(
    indexer_token="",
    indexer_address="https://testnet-algorand.api.purestake.io/idx2",
    headers=headers
)


def get_txn(address, start_time, end_time):

    response = myindexer.search_transactions_by_address(
        address=address,
        start_time=start_time,
        end_time=end_time
    )
    transactions = response["transactions"]
    txn_df = pd.DataFrame(transactions)
    return txn_df


def prepare_txn(txn_df):

    # Filter for payments
    txn_filtered = txn_df[txn_df["tx-type"] == "pay"]

    # Retrieve useful columns
    txn_df_reduced = txn_filtered[["payment-transaction", "sender"]]

    # Get amount info from transaction (amount is given in microAlgos)
    txn_df_reduced["amount"] = txn_df_reduced["payment-transaction"].apply(pd.Series)["amount"] / 1_000_000
    txn_df_reduced.drop(["payment-transaction"], axis=1, inplace=True)

    return txn_df_reduced


def group_txn_by_user(txn, total_tokens_to_pay):

    # Group txn by address
    txn_grouped = txn.groupby(["sender"]).sum()

    # Calculate amount % by address
    txn_grouped["amount_per"] = txn_grouped["amount"] / txn_grouped["amount"].sum()

    # Calculate tokens to pay to each address
    txn_grouped["tokens_to_pay"] = (txn_grouped["amount_per"] * total_tokens_to_pay)
    txn_grouped.sort_values(by=["tokens_to_pay"], ascending=False, inplace=True)

    return txn_grouped
