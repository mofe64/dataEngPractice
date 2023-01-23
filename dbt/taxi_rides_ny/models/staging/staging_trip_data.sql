{{ config(materialized='view') }}
-- ideally we should be selecting only the fields we want not all
select *,  {{ get_payment_type_description('payment_type') }} as payment_type_description
from {{source('staging', 'yellow_taxi_trips')}}
limit 100
