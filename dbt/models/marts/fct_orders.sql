with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select
        order_id,
        status as payment_status,
        amount as paid_amount,
        payment_gateway
    from {{ ref('stg_payments') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        o.order_date,
        o.status as order_status,
        o.total_amount,
        o.payment_method,
        p.payment_status,
        coalesce(p.paid_amount, 0) as paid_amount,
        p.payment_gateway
    from orders o
    left join payments p on o.order_id = p.order_id
)

select * from final
