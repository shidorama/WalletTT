# Possible fields: date, from, to, amount, balance
# Report parameters: wallet (required), start_date (not required),
# end_date (not required).
report_fields = ["date", "target_wallet_id", "state", "amount", "currency", "balance"]


def create_csv_report(report_rows):
    report_string_rows = [','.join(report_fields)]
    for report_entry in report_rows:
        entry_dict = report_entry.get_sanitized_object()
        report_string_rows.append(','.join([entry_dict.get(v, '') for v in report_fields]))
        return "\r\n".join(report_string_rows)
