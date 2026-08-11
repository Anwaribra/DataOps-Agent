with source as (
    select * from {{ source('raw_data', 'payments') }}
),

renamed as (
    select
        payment_id,
        order_id,
        payment_date::timestamp as payment_date,
        amount::numeric(10, 2) as amount,
        lower(trim(status)) as status,
        lower(trim(payment_gateway)) as payment_gateway
    from source
)

select * from renamed
