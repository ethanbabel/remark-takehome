# Remark Takehome

## How to Use

This project provides a pipeline for faceting product data, allowing users to suggest new facet values, propose entirely new facets, and apply facets to products. The pipeline can process products from a Shopify store or a local JSON file.

### Running the Pipeline

Before running the pipeline, ensure the following setup is complete:
1. **Set up your OpenAI API key**:
   - Create a `.env` file in the root directory of the project.
   - Add the following line to the `.env` file:
     ```
     OPENAI_KEY=<your_openai_api_key>
     ```
   - Replace `<your_openai_api_key>` with your actual OpenAI API key.

2. **Install dependencies**:
   - Run the following command to install all required Python packages:
     ```bash
     pip install -r requirements.txt
     ```
   - If installing via requirements.txt doesn't work for whatever reason, the main required dependencies for this project include: `python-dotenv`, `PyYAML`,`requests`, `typer`, `openai`, `spacy`, and `beautifulsoup4`.

To run the pipeline, use the following command in your terminal:

```bash
python3 cli.py --store-url <store_url> --output-file <output_file> --user-defined-facets <facet_config_file> --suggest-facet-values <option> --suggest-new-facets <option> --limit <limit>
```

### Command-Line Options

#### `--store-url`
- **Description**: The URL of the Shopify store to fetch products from.
- **Example**: `--store-url libertyskis.com`
- **Required**: Either `--store-url` or `--product-file` must be provided, but not both.

#### `--product-file`
- **Description**: Path to a local JSON file containing product data. (Note that all input files must be placed within the `input` directory, see the `input_examples` directory for example inputs)
- **Example**: `--product-file example_products.json`
- **Required**: Either `--store-url` or `--product-file` must be provided, but not both.

#### `--output-file`
- **Description**: Path to save the final labeled output. (Note that all outputs are saved in the `output` directory)
- **Default**: `labeled_products.json`
- **Example**: `--output-file labeled_products.json`

#### `--user-defined-facets`
- **Description**: Path to a YAML or JSON file defining user-defined facets. (Note that all input files must be placed within the `input` directory, see the `input_examples` directory for example inputs)
- **Example**: `--user-defined-facets example_config.yaml`
- **Required**: This is required. 

#### `--suggest-facet-values`
- **Description**: Whether to suggest new facet values for existing facets.
- **Options**:
  - `no`: Do not suggest new facet values.
  - `yes`: Automatically suggest new facet values.
  - `ask`: Prompt the user to decide whether to suggest new facet values for each facet.
- **Default**: `no`
- **Example**: `--suggest-facet-values ask`

#### `--suggest-new-facets`
- **Description**: Whether to suggest entirely new facets.
- **Options**:
  - `no`: Do not suggest new facets.
  - `yes`: Automatically suggest new facets.
  - `ask`: Prompt the user to decide whether to suggest new facets.
- **Default**: `no`
- **Example**: `--suggest-new-facets yes`

#### `--limit`
- **Description**: Limit the number of products to process.
- **Default**: 5 products.
- **Example**: `--limit 10`

### Example Usage

#### Process Products from a Shopify Store
```bash
python3 cli.py run --store-url libertyskis.com --output-file labeled_products.json --user-defined-facets example_config.yaml --suggest-facet-values ask --suggest-new-facets ask --limit 10
```

#### Process Products from a Local File
```bash
python3 cli.py run --product-file example_products.json --output-file labeled_products.json --user-defined-facets input_examples/example_config.yaml --suggest-facet-values yes --suggest-new-facets no
```

### User Defined Facets

The user-defined facets configuration file allows you to specify how products should be categorized. Each facet is defined with the following parameters:

#### Parameters for Each Facet

1. **`allowed_values`**
   - **Description**: A list of predefined values that the facet can take.
   - **Example**:
     ```yaml
     allowed_values:
       - Beginner
       - Intermediate
       - Advanced
     ```
   - **Notes**: These are the only values that will be assigned to products for this facet (along with the default value, if it's not included here) unless new values are suggested and accepted.

2. **`multi_valued`**
   - **Description**: Indicates whether a product can have multiple values for this facet.
   - **Options**:
     - `true`: A product can have multiple values for this facet.
     - `false`: A product can have only one value for this facet.

3. **`required`**
   - **Description**: Indicates whether this facet is required for all products.
   - **Options**:
     - `true`: Every product must have a value for this facet.
     - `false`: A product may or may not have a value for this facet.

4. **`default_value`**
   - **Description**: The default value to assign to a product if no value is determined for this facet.
   - **Options**:
     - Any value from the `allowed_values` list.
     - `null`: No default value is assigned.
   - **Example**:
     ```yaml
     default_value: Intermediate
     ```

---

## File Descriptions

### `cli.py`
- **Purpose**: Entry point for the command-line interface. Handles user inputs for the pipeline.

### `driver.py`
- **Purpose**: Drives the main pipeline logic, including loading products, suggesting facet values, proposing new facets, and applying facets to products.

### `product_loader.py`
- **Purpose**: Handles loading and normalizing product data from Shopify or a local JSON file.

### `facet_loader.py`
- **Purpose**: Loads and validates user-defined facet configurations from a YAML file.

### `facet_applier.py`
- **Purpose**: Applies facets to products based on user-defined configurations and suggestions.

### `suggest_facet_values.py`
- **Purpose**: Suggests new values for existing facets using OpenAI and product data.

### `suggest_new_facets.py`
- **Purpose**: Proposes entirely new facets and their allowed values using OpenAI and product data.

### `openai_client.py`
- **Purpose**: Provides methods for interacting with the OpenAI API, including suggesting facet values and new facets.

### `pos_tagging.py`
- **Purpose**: Extracts keywords from product descriptions using spaCy for natural language processing.

### `input_examples/example_products.json`
- **Purpose**: Example product data in JSON format for testing the pipeline.

### `input_examples/example_config.yaml`
- **Purpose**: Example facet configuration in YAML format for testing the pipeline.

---

## Notes
- Ensure you have the required dependencies installed, including `typer`, `openai`, `spacy`, and `beautifulsoup4`.
- Set your OpenAI API key in a `.env` file as `OPENAI_KEY=<your_api_key>`.
- Use the `--limit` option to process a subset of products for faster testing.

Let me know if you need further clarification or additional details!