import click
from datetime import datetime
from tabulate import tabulate

from app.db.engine import SessionLocal  # Change here, import the session factory
from app.services.sales_service import (
    create_sale,
    get_sale_by_id,
    get_all_sales,
    delete_sale,
    get_sales_summary_by_day,
    get_sales_summary_by_customer,
    get_sales_by_customer
)
from app.services.customer_service import get_customer_by_name, get_customer_by_id
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
    click.echo("7. View sales by customer")
    click.echo("8. Exit")
    try:
        return click.prompt("\nEnter a number", type=int)
    except click.exceptions.Abort:
        click.echo("\nAborted. Exiting.")
        exit()


def handle_create(db):
    try:
        identifier = click.prompt("Enter customer name (leave blank for Walk-In)", default="", show_default=False).strip()
        if not identifier:
            customer = get_customer_by_id(db, 1)
            if not customer:
                click.echo("❌ Walk-In Customer not found.")
                return
        else:
            matches = get_customer_by_name(db, identifier)
            if not matches:
                click.echo("❌ No customer found with that name.")
                return
            elif len(matches) > 1:
                click.echo("⚠️ Multiple customers found:")
                for c in matches:
                    click.echo(f"- ID {c.id}: {c.name}")
                selected_id = click.prompt("Enter the ID of the customer you meant", type=int)
                customer = next((c for c in matches if c.id == selected_id), None)
                if not customer:
                    click.echo("❌ Invalid selection.")
                    return
            else:
                customer = matches[0]

        click.echo(f"\nCreating sale for: {customer.name} (ID {customer.id})\n")

        products = get_all_products(db)
        if not products:
            click.echo("❌ No products available.")
            return

        product_table = [
            [p.id, p.name, p.brand, p.selling_price, p.stock, p.unit]
            for p in products
        ]
        headers = ["ID", "Name", "Brand", "Price", "Stock", "Unit"]
        click.echo(tabulate(product_table, headers=headers, tablefmt="fancy_grid"))

        items = []
        while True:
            product_id = click.prompt("Enter Product ID to add", type=int)
            product = next((p for p in products if p.id == product_id), None)
            if not product:
                click.echo("❌ Product not found.")
                continue
            if product.stock <= 0:
                click.echo("⚠️ Product is out of stock.")
                continue

            quantity = click.prompt(f"Enter quantity (Available: {product.stock})", type=int)
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
            click.echo("❌ No products added to the sale.")
            return

        sale = create_sale(db, customer.id, items)
        db.commit()

        click.echo(f"✅ Created sale #{sale.id} - Total: Ksh {sale.total_amount}")

    except Exception as e:
        db.rollback()
        click.echo(f"❌ Failed to create sale: {e}")


def handle_list(db):
    try:
        sales = get_all_sales(db)
        if not sales:
            click.echo("No sales found.")
            return
        for sale in sales:
            customer = get_customer_by_id(db, sale.customer_id)
            name_display = customer.name if customer else f"Unknown (ID {sale.customer_id})"
            click.echo(f"\U0001F9FE Sale #{sale.id}: Ksh {sale.total_amount} - {sale.timestamp} - Customer: {name_display}")
    except Exception as e:
        click.echo(f"❌ Failed to list sales: {e}")


def handle_view(db):
    try:
        sale_id = click.prompt("Sale ID", type=int)
        sale = get_sale_by_id(db, sale_id)
        if not sale:
            click.echo("❌ Sale not found.")
            return
        customer = get_customer_by_id(db, sale.customer_id)
        customer_name = customer.name if customer else f"Unknown (ID {sale.customer_id})"

        click.echo(f"\n\U0001F9FE Sale #{sale.id}")
        click.echo(f"Customer: {customer_name}")
        click.echo(f"Date: {sale.timestamp}")
        click.echo(f"Total: Ksh {sale.total_amount}")
        for item in sale.items:
            click.echo(f"- {item.name}: {item.quantity} x {item.price_at_sale}")
    except Exception as e:
        click.echo(f"❌ Error viewing sale: {e}")


def handle_delete(db):
    try:
        sale_id = click.prompt("Sale ID", type=int)
        delete_sale(db, sale_id)
        db.commit()
        click.echo(f"🗑️ Deleted sale #{sale_id}")
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Failed to delete sale: {e}")


def handle_summary_by_date(db):
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        summary = get_sales_summary_by_day(db, start, end)
        if not summary:
            click.echo("No sales summary found for the given date range.")
            return
        for row in summary:
            click.echo(f"{row['date']}: Ksh {row['total']}")
    except Exception as e:
        click.echo(f"❌ Failed to generate summary: {e}")


def handle_summary_by_customer(db):
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        summary = get_sales_summary_by_customer(db, start, end)
        if not summary:
            click.echo("No sales summary found for the given customers and date range.")
            return
        for row in summary:
            click.echo(f"{row['customer_name']}: Ksh {row['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to generate summary: {e}")


def handle_customer_sales(db):
    try:
        identifier = click.prompt("Enter customer ID or name")
        customer = None
        if identifier.isdigit():
            customer = get_customer_by_id(db, int(identifier))
        else:
            matches = get_customer_by_name(db, identifier)
            if not matches:
                click.echo("❌ No customer found.")
                return
            elif len(matches) > 1:
                click.echo("⚠️ Multiple customers found:")
                for c in matches:
                    click.echo(f"- ID {c.id}: {c.name}")
                selected_id = click.prompt("Enter the ID of the customer", type=int)
                customer = get_customer_by_id(db, selected_id)
            else:
                customer = matches[0]

        if not customer:
            click.echo("❌ Customer not found.")
            return

        sales = get_sales_by_customer(db, customer.id)
        if not sales:
            click.echo(f"No sales for {customer.name}.")
            return

        click.echo(f"\n\U0001F9FE Sales for {customer.name} (ID {customer.id}):\n")
        for sale in sales:
            click.echo(f"- Sale #{sale.id}: {sale.timestamp} - Ksh {sale.total_amount}")
            for item in sale.items:
                click.echo(f"  • {item.name}: {item.quantity} x {item.price_at_sale}")
            click.echo("")
    except Exception as e:
        click.echo(f"❌ Error fetching customer sales: {e}")


@click.command()
def cli():
    with SessionLocal() as db:  # Fixed here
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
                    handle_customer_sales(db)
                elif choice == 8:
                    click.echo("👋 Goodbye!")
                    break
                else:
                    click.echo("❌ Invalid option.")
            except click.exceptions.Abort:
                click.echo("\n👋 Exiting...")
                break
            except Exception as e:
                click.echo(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    cli()