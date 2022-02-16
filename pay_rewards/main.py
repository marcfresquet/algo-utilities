from get_transactions import get_txn, prepare_txn, group_txn_by_user
from do_transactions import pay_battery

from variables import my_wallet, total_tokens_to_pay, txn_start, txn_end


def pay_rewards():

    # Get txn done in address
    txn_df = get_txn(my_wallet, txn_start, txn_end)

    # Clean df and retrieve necessary info
    txn_cleaned = prepare_txn(txn_df)

    # Group paid amount by address and set earned rewards
    txn_grouped = group_txn_by_user(txn_cleaned, total_tokens_to_pay)

    # Pay rewards
    pay_battery(txn_grouped)


if __name__ == '__main__':
    pay_rewards()
