with customers as (
    select * from {{ ref('stg_customers') }}
),

customer_orders as (
    select * from {{ ref('int_customer_orders') }}
),

final as (
    select
        c.customer_id,
        c.first_name,
        c.last_name,
        c.email,
        c.created_at,
        c.status as customer_status,
        coalesce(co.total_orders, 0) as total_orders,
        coalesce(co.total_spent, 0) as total_spent,
        co.first_order_date,
        co.most_recent_order_date
    from customers c
    left join customer_orders co on c.customer_id = co.customer_id
)

select * from final
