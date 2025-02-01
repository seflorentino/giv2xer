import argparse
import calendar
import csv
import sys
from datetime import date

OUTPUT_COLS = [
    "*ContactName",
    "EmailAddress",
    "POAddressLine1",
    "POAddressLine2",
    "POAddressLine3",
    "POAddressLine4",
    "POCity",
    "PORegion",
    "POPostalCode",
    "POCountry",
    "*InvoiceNumber",
    "Reference",
    "*InvoiceDate",
    "*DueDate",
    "InventoryItemCode",
    "*Description",
    "*Quantity",
    "*UnitAmount",
    "Discount",
    "*AccountCode",
    "*TaxType",
    "TrackingName1",
    "TrackingOption1",
    "TrackingName2",
    "TrackingOption2",
    "Currency",
    "BrandingTheme",
]


def format_date(dt):
    return dt.strftime("%m/%d/%Y")


def format_date_str(dt_str):
    return format_date(date.fromisoformat(dt_str))


def format_date_str_to_eod(dt_str):
    dt = format_date(date.fromisoformat(dt_str))
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    return dt.replace(day=last_day)


def g2x(csv_reader, description, account_code, tax_type, due_date_eom):
    output = []

    for row in csv_reader:
        out_row = {
            "*ContactName": row["First Name"] + " " + row["Last Name"],
            "EmailAddress": row["Email"],
            "*InvoiceNumber": row["Receipt#"],
            "Reference": row["Receipt#"],
            "*InvoiceDate": format_date_str(row["Date"]),
            "*DueDate": (format_date_str_to_eod if due_date_eom else format_date_str)(
                row["Date"]
            ),
            "InventoryItemCode": row["Ext Fund Name"],
            "*Description": description,
            "*Quantity": 1,
            "*UnitAmount": row["Amount"],
            "*AccountCode": account_code,
            "*TaxType": tax_type,
        }
        output.append(out_row)

    return sorted(output, key=lambda row: row["*InvoiceNumber"])


def write_csv(writer, output):
    writer.writeheader()
    for row in output:
        writer.writerow(row)


def main():
    parser = argparse.ArgumentParser(description="Givelify report to Xero import")

    parser.add_argument("input_file", help="Input file path")

    parser.add_argument(
        "--description",
        required=True,
        type=str,
        metavar="description",
        help="Invoice description",
    )

    parser.add_argument(
        "--account-code",
        required=True,
        type=str,
        metavar="account_code",
        help="Xero account code",
    )

    parser.add_argument(
        "--tax-type",
        type=str,
        metavar="tax_type",
        default="Tax Exempt",
        help="Tax type",
    )

    parser.add_argument(
        "--due-date-eom",
        action=argparse.BooleanOptionalAction,
        metavar="due_date_eom",
        help="Set due date to end of month",
    )

    parser.add_argument(
        "--output",
        type=str,
        metavar="file_name",
        default=None,
        help="Output file path",
    )

    args = parser.parse_args()

    with open(args.input_file) as csv_file:
        csv_reader = csv.DictReader(csv_file)
        output = g2x(
            csv_reader,
            args.description,
            args.account_code,
            args.tax_type,
            args.due_date_eom,
        )

    if args.output:
        with open(args.output, "w", newline="") as f:
            csv_writer = csv.DictWriter(f, fieldnames=OUTPUT_COLS)
            write_csv(csv_writer, output)
    else:
        csv_writer = csv.DictWriter(sys.stdout, fieldnames=OUTPUT_COLS)
        write_csv(csv_writer, output)


if __name__ == "__main__":
    main()
