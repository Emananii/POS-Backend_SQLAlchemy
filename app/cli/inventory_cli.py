import click
from app.models.product import Product  # Import Product model
from app.models.category import Category  # Import Category model
from app.services.inventory_service import (
    create_product,
    update_product,
    get_product_by_id,
    get_all_products,
    create_category,
    update_category,
    search_products_by_name,
    get_products_by_category,
    get_products_in_stock,
    delete_product
)
from app.db.engine import SessionLocal


def get_db():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_product_cli():
    """Add a new product to the inventory."""
    click.echo("\n--- Add New Product ---")
    name = click.prompt('Enter product name')
    brand = click.prompt('Enter product brand')
    purchase_price = click.prompt('Enter purchase price', type=float)
    selling_price = click.prompt('Enter selling price', type=float)
    stock = click.prompt('Enter stock quantity', type=int)
    barcode = click.prompt('Enter barcode')
    category_id = click.prompt('Enter category ID', type=int)
    unit = click.prompt('Enter unit of measurement')

    db = next(get_db())
    try:
        product = create_product(
            db,
            name=name,
            brand=brand,
            purchase_price=purchase_price,
            selling_price=selling_price,
            stock=stock,
            barcode=barcode,
            category_id=category_id,
            unit=unit
        )
        click.echo(f"Product '{product.name}' added successfully with ID: {product.id}.")
    except Exception as e:
        click.echo(f"Error adding product: {e}")


def update_product_cli():
    """Update product details."""
    click.echo("\n--- Update Product ---")
    product_id = click.prompt('Enter product ID to update', type=int)
    db = next(get_db())
    product = get_product_by_id(db, product_id)

    if not product:
        click.echo(f"Product with ID {product_id} not found.")
        return

    click.echo(f"Current details for Product ID {product_id}:")
    click.echo(f"  Name: {product.name}")
    click.echo(f"  Brand: {product.brand}")
    click.echo(f"  Purchase Price: {product.purchase_price}")
    click.echo(f"  Selling Price: {product.selling_price}")
    click.echo(f"  Stock: {product.stock}")
    click.echo(f"  Barcode: {product.barcode}")
    click.echo(f"  Category ID: {product.category_id}")
    click.echo(f"  Unit: {product.unit}")

    name = click.prompt(f'Enter new name (current: {product.name})', default=product.name)
    brand = click.prompt(f'Enter new brand (current: {product.brand})', default=product.brand)
    purchase_price = click.prompt(f'Enter new purchase price (current: {product.purchase_price})', default=product.purchase_price, type=float)
    selling_price = click.prompt(f'Enter new selling price (current: {product.selling_price})', default=product.selling_price, type=float)
    stock = click.prompt(f'Enter new stock quantity (current: {product.stock})', default=product.stock, type=int)
    barcode = click.prompt(f'Enter new barcode (current: {product.barcode})', default=product.barcode)
    category_id = click.prompt(f'Enter new category ID (current: {product.category_id})', default=product.category_id, type=int)
    unit = click.prompt(f'Enter new unit (current: {product.unit})', default=product.unit)

    try:
        updated_product = update_product(
            db,
            product_id=product_id,
            name=name,
            brand=brand,
            purchase_price=purchase_price,
            selling_price=selling_price,
            stock=stock,
            barcode=barcode,
            category_id=category_id,
            unit=unit
        )
        click.echo(f"Product '{updated_product.name}' updated successfully.")
    except Exception as e:
        click.echo(f"Error updating product: {e}")


def list_products():
    """List all products in the inventory."""
    click.echo("\n--- All Products ---")
    db = next(get_db())
    products = get_all_products(db)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, "
                       f"Price: ${product.selling_price:.2f}, Stock: {product.stock} {product.unit}, "
                       f"Category ID: {product.category_id}, Barcode: {product.barcode}")
    else:
        click.echo("No products found in the inventory.")


def create_category_cli():
    """Create a new product category."""
    click.echo("\n--- Create New Category ---")
    name = click.prompt('Enter category name')
    db = next(get_db())
    try:
        category = create_category(db, name=name)
        click.echo(f"Category '{category.name}' created successfully with ID: {category.id}.")
    except Exception as e:
        click.echo(f"Error creating category: {e}")


def update_category_cli():
    """Update category details."""
    click.echo("\n--- Update Category ---")
    category_id = click.prompt('Enter category ID to update', type=int)
    name = click.prompt('Enter new category name')
    db = next(get_db())
    try:
        updated_category = update_category(db, category_id=category_id, name=name)
        if updated_category:
            click.echo(f"Category ID {category_id} updated to '{updated_category.name}' successfully.")
        else:
            click.echo(f"Category with ID {category_id} not found.")
    except Exception as e:
        click.echo(f"Error updating category: {e}")


def search_product_by_name(name_query):
    """Search for products by name."""
    click.echo(f"\n--- Searching for products with name '{name_query}' ---")
    db = next(get_db())
    products = search_products_by_name(db, name_query)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, "
                       f"Price: ${product.selling_price:.2f}, Stock: {product.stock} {product.unit}")
    else:
        click.echo(f"No products found matching '{name_query}'.")


def list_products_by_category(category_id):
    """List products belonging to a specific category."""
    click.echo(f"\n--- Products in Category ID {category_id} ---")
    db = next(get_db())
    products = get_products_by_category(db, category_id)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Brand: {product.brand}, "
                       f"Price: ${product.selling_price:.2f}, Stock: {product.stock} {product.unit}")
    else:
        click.echo(f"No products found for category ID {category_id}.")


def view_product_stock_levels():
    """View stock levels for all products."""
    click.echo("\n--- Product Stock Levels ---")
    db = next(get_db())
    products = get_products_in_stock(db)
    if products:
        for product in products:
            click.echo(f"ID: {product.id}, Name: {product.name}, Stock: {product.stock} {product.unit}")
    else:
        click.echo("No products with stock information found.")


def delete_product_cli():
    """Delete a product from the inventory."""
    click.echo("\n--- Delete Product ---")
    product_id = click.prompt('Enter product ID to delete', type=int)
    db = next(get_db())
    try:
        deleted = delete_product(db, product_id)
        if deleted:
            click.echo(f"Product with ID {product_id} deleted successfully.")
        else:
            click.echo(f"Product with ID {product_id} not found.")
    except Exception as e:
        click.echo(f"Error deleting product: {e}")


def inventory_menu():
    """Displays the main inventory CLI menu options."""
    click.echo("\n🧾 INVENTORY CLI MENU")
    click.echo("1. Add a new product")
    click.echo("2. Update a product")
    click.echo("3. List all products")
    click.echo("4. Create a new category")
    click.echo("5. Update a category")
    click.echo("6. Search for a product by name")
    click.echo("7. List products by category")
    click.echo("8. View product stock levels")
    click.echo("9. Delete a product")
    click.echo("10. Exit")


@click.command()
def main_menu(): 
    """Main menu for inventory management."""
    while True:
        inventory_menu()  
        try:
            choice = click.prompt("Enter a number", type=int)
        except click.Abort:
            click.echo("\nExiting due to user interruption.")
            break
        except ValueError:
            click.echo("Invalid input. Please enter a number.")
            continue

        if choice == 1:
            add_product_cli()
        elif choice == 2:
            update_product_cli()
        elif choice == 3:
            list_products()
        elif choice == 4:
            create_category_cli()
        elif choice == 5:
            update_category_cli()
        elif choice == 6:
            name = click.prompt("Enter product name to search")
            search_product_by_name(name)
        elif choice == 7:
            category_id = click.prompt("Enter category ID to list products", type=int)
            list_products_by_category(category_id)
        elif choice == 8:
            view_product_stock_levels()
        elif choice == 9:
            delete_product_cli()
        elif choice == 10:
            click.echo("Exiting the menu...")
            break
        else:
            click.echo("Invalid option, please select a valid choice.")


if __name__ == '__main__':
    main_menu()
