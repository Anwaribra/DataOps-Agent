with source as (
    select * from {{ source('raw_data', 'orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        order_date::timestamp as order_date,
        lower(trim(status)) as status,
        total_amount::numeric(10, 2) as total_amount,
        lower(trim(payment_method)) as payment_method
    from source
)

select * from renamed
