with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select * from {{ ref('stg_payments') }}
),

customer_orders as (
    select
        o.customer_id,
        count(o.order_id) as total_orders,
        sum(case when o.status in ('completed', 'shipped') then o.total_amount else 0 end) as total_spent,
        min(o.order_date) as first_order_date,
        max(o.order_date) as most_recent_order_date
    from orders o
    group by o.customer_id
)

select * from customer_orders
