with source as (
    select * from {{ source('raw_data', 'products') }}
),

renamed as (
    select
        product_id,
        trim(name) as product_name,
        trim(category) as category,
        price::numeric(10, 2) as price,
        stock_quantity::integer as stock_quantity,
        created_at::timestamp as created_at
    from source
)

select * from renamed
