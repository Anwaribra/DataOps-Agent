with source as (
    select * from {{ source('raw_data', 'customers') }}
),

renamed as (
    select
        customer_id,
        trim(first_name) as first_name,
        trim(last_name) as last_name,
        lower(trim(email)) as email,
        created_at::timestamp as created_at,
        lower(trim(status)) as status
    from source
)

select * from renamed
