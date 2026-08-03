# Lab 1B Data Dictionary

## Transaction fields after harmonization

| Field | Description |
|---|---|
| sale_line_id | Unique identifier for a sale line |
| sale_date | Date of the sale |
| store_id | Branch identifier |
| product_id | Product identifier |
| quantity | Units sold |
| unit_price | Price before discount |
| promotion_code | Promotion applied, when applicable |
| payment_method | Card, Cash, or Transfer |

## Reference files
- products.csv: product master and category.
- stores.csv: branch, city, and region.
- promotions.csv: campaign dates and discount percentages.
- monthly_targets.csv: sales goal for each branch and month.

The three branch transaction files use different formats and schemas. The pipeline must harmonize them into one common schema.
