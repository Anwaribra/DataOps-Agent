with products as (
    select * from {{ ref('stg_products') }}
)

select
    product_id,
    product_name,
    category,
    price,
    stock_quantity,
    created_at
from products
