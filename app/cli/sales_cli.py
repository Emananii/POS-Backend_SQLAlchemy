import click
from datetime import datetime
from tabulate import tabulate
from app.db.engine import SessionLocal
from app.services.sales_service import (
    create_sale,
    get_sale_by_id,
    get_all_sales,
    delete_sale,
    get_sales_summary_by_day,
    get_recent_sales

)
from app.services.customer_service import (
    get_customer_by_name,
    get_customer_by_id,
    get_all_customers,
    get_purchases_by_customer
)

from app.services.inventory_service import get_all_products


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise click.BadParameter("Invalid date format. Use YYYY-MM-DD.")


def menu():
    click.echo("\n\U0001F4B0 SALES CLI MENU")
    click.echo("1. Create a new sale")
    click.echo("2. List all sales")
    click.echo("3. View a sale by ID")
    click.echo("4. Delete a sale")
    click.echo("5. Sales summary by date")
    click.echo("6. Sales summary by customer")
    click.echo("7. Exit")
    try:
        return click.prompt("\nEnter a number", type=int)
    except click.exceptions.Abort:
        click.echo("\nAborted. Exiting.")
        exit()


def handle_create(db):
    try:
        customers = get_all_customers(db)
        if not customers:
            click.echo("No customers available in the system.")
            return

        customer_table = [[c.id, c.name] for c in customers]
        headers = ["ID", "Customer Name"]

        click.echo("\nAvailable Customers:")
        click.echo(tabulate(customer_table,
                   headers=headers, tablefmt="fancy_grid"))

        identifier = click.prompt(
            "Enter customer ID or name (leave blank for Walk-In)",
            default="", show_default=False
        ).strip()

        # 🧍 Handle Walk-In
        if not identifier:
            customer = get_customer_by_id(db, 1)
            if not customer:
                click.echo("Walk-In Customer (ID 1) not found.")
                return

        elif identifier.isdigit():
            customer = get_customer_by_id(db, int(identifier))
            if not customer:
                click.echo(f"No customer found with ID {identifier}.")
                return

        else:
            matches = get_customer_by_name(db, identifier)
            if not matches:
                click.echo("No customer found with that name.")
                return
            elif len(matches) > 1:
                click.echo("⚠️ Multiple customers found:")
                for c in matches:
                    click.echo(f"- ID {c.id}: {c.name}")
                selected_id = click.prompt(
                    "Enter the ID of the customer you meant", type=int)
                customer = next(
                    (c for c in matches if c.id == selected_id), None)
                if not customer:
                    click.echo("Invalid selection.")
                    return
            else:
                customer = matches[0]

        click.echo(
            f"\nCreating sale for: {customer.name} (ID {customer.id})\n")

        products = get_all_products(db)
        if not products:
            click.echo("No products available.")
            return

        product_table = [
            [p.id, p.name, p.brand, p.selling_price, p.stock, p.unit]
            for p in products
        ]
        headers = ["ID", "Name", "Brand", "Price", "Stock", "Unit"]
        click.echo(
            tabulate(product_table, headers=headers, tablefmt="fancy_grid"))

        items = []
        while True:
            product_id = click.prompt("Enter Product ID to add", type=int)
            product = next((p for p in products if p.id == product_id), None)
            if not product:
                click.echo("Product not found.")
                continue
            if product.stock <= 0:
                click.echo("⚠️ Product is out of stock.")
                continue

            quantity = click.prompt(
                f"Enter quantity (Available: {product.stock})", type=int)
            if quantity > product.stock:
                click.echo(f"⚠️ Only {product.stock} units available.")
                continue

            items.append({
                "product_id": product.id,
                "quantity": quantity,
                "price_at_sale": product.selling_price,
                "name": product.name
            })

            if not click.confirm("Add another product?"):
                break

        if not items:
            click.echo("No products added to the sale.")
            return

        sale = create_sale(db, customer.id, items)
        db.commit()

        click.echo(
            f"✅ Created sale #{sale.id} - Total: Ksh {sale.total_amount}")

    except Exception as e:
        db.rollback()
        click.echo(f"Failed to create sale: {e}")


def handle_list(db):
    try:
        sales = get_all_sales(db)
        if not sales:
            click.echo("No sales found.")
            return

        table_data = []

        for sale in sales:
            customer = get_customer_by_id(db, sale.customer_id)
            name_display = customer.name if customer else f"Unknown (ID {sale.customer_id})"

            num_items = len(sale.sale_items) if hasattr(
                sale, "sale_items") else "?"

            table_data.append([
                sale.id,
                name_display,
                f"Ksh {sale.total_amount}",
                sale.timestamp.strftime("%Y-%m-%d %H:%M"),
                num_items
            ])

        headers = ["Sale ID", "Customer", "Total Amount", "Timestamp", "Items"]

        click.echo("\nSales Summary:\n")
        click.echo(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

    except Exception as e:
        click.echo(f" Failed to list sales: {e}")


def handle_view(db, limit=10):
    try:

        sales = get_recent_sales(db, limit=limit)

        if not sales:
            click.echo("No sales found.")
            return

        sales_table = [
            [sale.id, sale.timestamp.strftime("%Y-%m-%d %H:%M:%S")]
            for sale in sales
        ]
        headers = ["Sale ID", "Timestamp"]
        click.echo("\nRecent Sales:")
        click.echo(tabulate(sales_table, headers=headers, tablefmt="fancy_grid"))

        sale_ids = {sale.id for sale in sales}
        while True:
            sale_id = click.prompt("Enter Sale ID to view details", type=int)
            if sale_id in sale_ids:
                break
            else:
                click.echo(
                    "Invalid Sale ID. Please select from the list above.")

        sale = get_sale_by_id(db, sale_id)
        if not sale:
            click.echo("Sale not found.")
            return

        customer = get_customer_by_id(db, sale.customer_id)
        customer_name = customer.name if customer else f"Unknown (ID {sale.customer_id})"

        click.echo(f"\n\U0001F9FE Sale #{sale.id}")
        click.echo(f"Customer: {customer_name}")
        click.echo(f"Date: {sale.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        click.echo(f"Total: Ksh {sale.total_amount}")

        items_table = [
            [item.name, item.quantity, item.price_at_sale,
                item.quantity * item.price_at_sale]
            for item in sale.items
        ]
        item_headers = ["Product", "Quantity", "Price at Sale", "Total"]
        click.echo(
            tabulate(items_table, headers=item_headers, tablefmt="fancy_grid"))

    except Exception as e:
        click.echo(f"Error viewing sale: {e}")


def handle_delete(db):
    try:

        recent_sales = get_recent_sales(db, limit=7)
        if not recent_sales:
            click.echo("No recent sales found.")
            return

        table = [
            (
                sale.id,
                sale.timestamp.strftime("%Y-%m-%d %H:%M"),
                f"Ksh {sale.total_amount:,.2f}",
                sale.customer.name if sale.customer else "Guest"
            )
            for sale in recent_sales
        ]
        click.echo("\nOnly the 7 most recent sales can be deleted:\n")
        click.echo(tabulate(table, headers=[
                   "Sale ID", "Date", "Total", "Customer"], tablefmt="fancy_grid"))

        while True:

            sale_id = click.prompt("Enter the Sale ID to delete", type=int)

            sale_ids = [s.id for s in recent_sales]
            if sale_id not in sale_ids:
                click.echo(
                    "⚠️ You can only delete from the 7 most recent sales. Try again.")
                continue

            if not click.confirm(f"Are you absolutely sure you want to delete sale #{sale_id}?", default=False):
                click.echo("❎ Deletion cancelled.")
            else:
                try:
                    delete_sale(db, sale_id)
                    db.commit()
                    click.echo(f"✅ Sale #{sale_id} deleted.")
                except Exception as e:
                    db.rollback()
                    click.echo(f"Failed to delete sale: {e}")

            if not click.confirm("Delete another sale?", default=False):
                break

    except Exception as e:
        db.rollback()
        click.echo(f"Error during sale deletion: {e}")


def handle_summary_by_date(db):
    try:
        start = parse_date(click.prompt(
            "Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)",
                         default="", show_default=False))
        summary = get_sales_summary_by_day(db, start, end)
        if not summary:
            click.echo("No sales summary found for the given date range.")
            return
        for row in summary:
            click.echo(f"{row['date']}: Ksh {row['total']}")
    except Exception as e:
        click.echo(f"Failed to generate summary: {e}")


def handle_summary_by_customer(db):
    try:
        customers = get_all_customers(db)
        if not customers:
            click.echo("No customers found.")
            return

        table = [(c.id, c.name, c.email or "-", c.customer_type)
                 for c in customers]
        click.echo(tabulate(table, headers=[
                   "ID", "Name", "Email", "Type"], tablefmt="fancy_grid"))

        customer_id = click.prompt(
            "Enter the Customer ID to view summary", type=int)
        try:
            customer = get_customer_by_id(db, customer_id)
        except ValueError as ve:
            click.echo(f"{ve}")
            return

        if click.confirm("Do you want to filter by date range?", default=False):
            start_input = click.prompt(
                "Start date (YYYY-MM-DD)", default="", show_default=False)
            end_input = click.prompt(
                "End date (YYYY-MM-DD)", default="", show_default=False)

            start_date = parse_date(start_input) if start_input else None
            end_date = parse_date(end_input) if end_input else None
        else:
            start_date = end_date = None

        purchases = get_purchases_by_customer(db, customer_id)
        if not purchases:
            click.echo(f"📭 No purchases found for customer '{customer.name}'.")
            return

        if start_date or end_date:
            purchases = [
                sale for sale in purchases
                if (not start_date or sale.timestamp >= start_date)
                and (not end_date or sale.timestamp <= end_date)
            ]

        if not purchases:
            click.echo(f"No purchases found for that date range.")
            return

        total_sales = sum(sale.total_amount for sale in purchases)
        num_sales = len(purchases)

        click.echo("\n Customer Sales Summary")
        click.echo(f" Name       : {customer.name}")
        click.echo(f" Email      : {customer.email}")
        click.echo(f" Phone      : {customer.phone or 'N/A'}")
        click.echo(f" Purchases  : {num_sales}")
        click.echo(f" Total Sales: Ksh {total_sales:,.2f}")

        if click.confirm("Show purchase breakdown?", default=False):
            breakdown_table = [
                (sale.id, sale.timestamp.strftime("%Y-%m-%d %H:%M"),
                 f"Ksh {sale.total_amount:,.2f}")
                for sale in purchases
            ]
            click.echo(tabulate(breakdown_table, headers=[
                       "Sale ID", "Date", "Amount"], tablefmt="grid"))

    except Exception as e:
        click.echo(f"Error fetching customer summary: {e}")


@click.command()
def cli():
    with SessionLocal() as db:
        while True:
            try:
                choice = menu()
                if choice == 1:
                    handle_create(db)
                elif choice == 2:
                    handle_list(db)
                elif choice == 3:
                    handle_view(db)
                elif choice == 4:
                    handle_delete(db)
                elif choice == 5:
                    handle_summary_by_date(db)
                elif choice == 6:
                    handle_summary_by_customer(db)
                elif choice == 7:
                    click.echo("Goodbye Friend!")
                    break
                else:
                    click.echo("Invalid option.")
            except click.exceptions.Abort:
                click.echo("\n Exiting...")
                break
            except Exception as e:
                click.echo(f"Unexpected error: {e}")


if __name__ == "__main__":
    cli()
