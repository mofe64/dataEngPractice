{{ config(materialized='view') }}
-- ideally we should be selecting only the fields we want not all
select *,
{{ dbt_utils.surrogate_key(['tpep_pickup_datetime']) }} as tripid, -- this macro is from the dbt_utils dep we installed, will ally md5 hash fn to params, concat the results to one string and return
{{ get_payment_type_description('payment_type') }} as payment_type_description
from {{source('staging', 'yellow_taxi_trips')}}
-- we give the is_test_run var a default value of true
{% if var('is_test_run', default=true) %}

  limit 100

{% endif %}
-- if we want to override this var when running model we can do so via the cmd as follows
-- dbt build --m <model.sql> --var 'is_test_run: false'
-- or
-- dbt run --select model_file_name --var 'is_test_run: false'
-- or 
-- dbt run --var 'is_test_run: false'
