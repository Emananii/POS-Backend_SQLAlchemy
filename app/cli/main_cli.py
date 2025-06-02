import click
from app.db.engine import SessionLocal
from app.cli.sales_cli import menu as sales_menu
from app.cli.customer_cli import menu as customer_menu
from app.cli.inventory_cli import menu as inventory_menu


def main_menu():
    click.echo("\n🧭 MAIN MENU")
    click.echo("1. Point of Sale")
    click.echo("2. Inventory")
    click.echo("3. Customers")
    click.echo("4. Exit")

    try:
        return click.prompt("\nEnter a number", type=int)
    except click.exceptions.Abort:
        click.echo("\nAborted. Exiting.")
        exit()


def run():
    while True:
        choice = main_menu()
        if choice == 1:
            run_app_cli_sales_cli()
        elif choice == 2:
            run_app_cli_inventory_cli()
        elif choice == 3:
            run_app_cli_customer_cli() 
        elif choice == 4:
            click.echo("👋 Goodbye.")
            break
        else:
            click.echo("❌ Invalid selection. Try again.")


def run_app_cli_sales_cli():
    db = SessionLocal()
    try:
        while True:
            option = sales_menu()
            if option == 1:
                from app.cli.sales_cli import handle_create
                handle_create(db)
            elif option == 2:
                from app.cli.sales_cli import handle_list
                handle_list(db)
            elif option == 3:
                from app.cli.sales_cli import handle_view
                handle_view(db)
            elif option == 4:
                from app.cli.sales_cli import handle_delete
                handle_delete(db)
            elif option == 5:
                from app.cli.sales_cli import handle_summary_by_date
                handle_summary_by_date(db)
            elif option == 6:
                from app.cli.sales_cli import handle_summary_by_customer
                handle_summary_by_customer(db)
            elif option == 7:
                click.echo("🔙 Returning to Main Menu.")
                break
            else:
                click.echo("❌ Invalid option.")
    finally:
        db.close()

def run_app_cli_inventory_cli():
    db = SessionLocal()
    try:
        while True:
            option = inventory_menu()
            if option == 1:
                from app.cli.inventory_cli import add_product_cli
                add_product_cli(db)
            elif option == 2:
                from app.cli.inventory_cli import update_product_cli
                update_product_cli(db)
            elif option == 3:
                from app.cli.inventory_cli import list_products
                list_products(db)
            elif option == 4:
                from app.cli.inventory_cli import purchase_stock_cli
                purchase_stock_cli(db)
            elif option == 5:
                from app.cli.inventory_cli import create_category_cli
                create_category_cli(db)
            elif option == 6:
                from app.cli.inventory_cli import update_category_cli
                update_category_cli(db)
            elif option == 7:
                click.echo("🔙 Returning to Main Menu.")
                break
            else:
                click.echo("❌ Invalid option. Please try again.")
    finally:
        db.close()



def run_app_cli_customer_cli():
    db = SessionLocal()
    try:
        while True:
            option = customer_menu()
            if option == 1:
                from app.cli.customer_cli import handle_create
                handle_create(db)
            elif option == 2:
                from app.cli.customer_cli import handle_list
                handle_list(db)
            elif option == 3:
                from app.cli.customer_cli import handle_view
                handle_view(db)
            elif option == 4:
                from app.cli.customer_cli import handle_update
                handle_update(db)
            elif option == 5:
                from app.cli.customer_cli import handle_delete
                handle_delete(db)
            elif option == 6:
                from app.cli.customer_cli import handle_loyalty
                handle_loyalty(db)
            elif option == 7:
                from app.cli.customer_cli import handle_discount
                handle_discount(db)
            elif option == 8:
                from app.cli.customer_cli import handle_view_purchases
                handle_view_purchases(db)
            elif option == 9:
                from app.cli.customer_cli import handle_top_customers
                handle_top_customers(db)
            elif option == 10:
                from app.cli.customer_cli import handle_total_sales
                handle_total_sales(db)
            elif option == 11:
                from app.cli.customer_cli import handle_purchase_frequency
                handle_purchase_frequency(db)
            elif option == 12:
                click.echo("🔙 Returning to Main Menu.")
                break
            else:
                click.echo("❌ Invalid option.")
    finally:
        db.close()

if __name__ == "__main__":
    run()