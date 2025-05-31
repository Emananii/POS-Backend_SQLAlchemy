import click
from datetime import datetime
from app.services.sales_service import (
    create_sale,
    get_sale_by_id,
    get_all_sales,
    delete_sale,
    get_sales_summary_by_day,          # ✅ updated import
    get_sales_summary_by_customer      # ✅ updated import
)

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str) if date_str else None
    except ValueError:
        raise click.BadParameter("Invalid date format. Use YYYY-MM-DD.")

def menu():
    click.echo("\n💰 SALES CLI MENU")
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

def handle_create():
    try:
        customer_id = click.prompt("Customer ID", type=int)
        items = []
        while True:
            product_id = click.prompt("Product ID", type=int)
            quantity = click.prompt("Quantity", type=int)
            items.append({"product_id": product_id, "quantity": quantity})
            if not click.confirm("Add another product?"):
                break
        sale = create_sale(customer_id, items)
        click.echo(f"✅ Created sale #{sale.id} - Total: Ksh {sale.total_amount}")
    except Exception as e:
        click.echo(f"❌ Failed to create sale: {e}")

def handle_list():
    try:
        sales = get_all_sales()
        if not sales:
            click.echo("No sales found.")
            return
        for sale in sales:
            click.echo(f"🧾 Sale #{sale.id}: Ksh {sale.total_amount} - {sale.timestamp} (Customer ID: {sale.customer_id})")
    except Exception as e:
        click.echo(f"❌ Failed to list sales: {e}")

def handle_view():
    try:
        sale_id = click.prompt("Sale ID", type=int)
        sale = get_sale_by_id(sale_id)
        if not sale:
            click.echo("❌ Sale not found.")
            return
        click.echo(f"🧾 Sale #{sale.id}")
        click.echo(f"Customer ID: {sale.customer_id}")
        click.echo(f"Date: {sale.timestamp}")
        click.echo(f"Total: Ksh {sale.total_amount}")
        for item in sale.items:
            click.echo(f"- {item.name}: {item.quantity} x {item.price_at_sale}")
    except Exception as e:
        click.echo(f"❌ Error viewing sale: {e}")

def handle_delete():
    try:
        sale_id = click.prompt("Sale ID", type=int)
        delete_sale(sale_id)
        click.echo(f"🗑️ Deleted sale #{sale_id}")
    except Exception as e:
        click.echo(f"❌ Failed to delete sale: {e}")

def handle_summary_by_date():
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        summary = get_sales_summary_by_day(start, end)
        for row in summary:
            click.echo(f"{row['date']}: Ksh {row['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to generate summary: {e}")

def handle_summary_by_customer():
    try:
        start = parse_date(click.prompt("Start date (YYYY-MM-DD)", default="", show_default=False))
        end = parse_date(click.prompt("End date (YYYY-MM-DD)", default="", show_default=False))
        summary = get_sales_summary_by_customer(start, end)
        for row in summary:
            click.echo(f"{row['customer_name']}: Ksh {row['total_sales']}")
    except Exception as e:
        click.echo(f"❌ Failed to generate summary: {e}")

@click.command()
def cli():
    while True:
        try:
            choice = menu()
            if choice == 1: handle_create()
            elif choice == 2: handle_list()
            elif choice == 3: handle_view()
            elif choice == 4: handle_delete()
            elif choice == 5: handle_summary_by_date()
            elif choice == 6: handle_summary_by_customer()
            elif choice == 7:
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
