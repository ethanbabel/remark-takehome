import typer
from driver import run_full_pipeline

INPUT_FOLDER = "input/"
OUTPUT_FOLDER = "output/"
DEFAULT_OUTPUT_FILE = "labeled_products.json"

app = typer.Typer()

@app.command()
def run(
    store_url: str = typer.Option(None, help="URL of the Shopify store (e.g. libertyskis.com)"),
    product_file: str = typer.Option(None, help="Path to a local JSON file of products"),
    output_file: str = typer.Option(None, help="Where to save the final labeled output"),
    user_defined_facets: str = typer.Option(None, help="Path to YAML/JSON file of user-defined facets"),
    suggest_facet_values: str = typer.Option(
        "no",
        help="Suggest new facet values: 'no', 'yes', or 'ask'.",
        case_sensitive=False
    ),
    suggest_new_facets: str = typer.Option(
        "no",
        help="Suggest entirely new facets: 'no', 'yes', or 'ask'.",
        case_sensitive=False
    ),
    limit: int = typer.Option(
        5,
        help="Limit the number of products to be faceted. If not specified, all products will be processed."
    )
):
    """
    Run the full product faceting pipeline, optionally suggesting new facet values and new facets.
    For suggestion options, use 'no', 'yes', or 'ask'.
    """
    if not output_file:
        output_file = DEFAULT_OUTPUT_FILE
    output_file = OUTPUT_FOLDER + output_file

    if (store_url and product_file) or (not store_url and not product_file):
        typer.echo("Error: You must specify exactly one of --store-url or --product-file.")
        raise typer.Exit(code=1)

    if product_file:
        product_file = INPUT_FOLDER + product_file
    if user_defined_facets:
        user_defined_facets = INPUT_FOLDER + user_defined_facets

    if not user_defined_facets:
        if suggest_facet_values.lower() in ("yes", "ask"):
            typer.echo("Error: Cannot suggest facet values without a user-defined facets config file.")
            raise typer.Exit(code=1)
        if suggest_new_facets.lower() == "no":
            typer.echo("Error: No user-defined facets provided and suggesting new facets is disabled. Nothing to do.")
            raise typer.Exit(code=1)

    run_full_pipeline(
        store_url=store_url,
        product_file=product_file,
        output_file=output_file,
        user_defined_facets=user_defined_facets,
        suggest_facet_values_option=suggest_facet_values,
        suggest_new_facets_option=suggest_new_facets,
        limit=limit
    )

if __name__ == "__main__":
    app()