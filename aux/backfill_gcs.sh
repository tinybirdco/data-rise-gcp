TB_HOST=<region:api.tinybird.co|api.us-east.tinybird.co>
TB_TOKEN=<your token with append rights to DS>
DATA_SOURCE_NAME=ecom_events

backfill_files="https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_1_30M.parquet
https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_2_20M.parquet
https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_3_13M.parquet
https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_4_16M.parquet
https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_5_13M.parquet
https://storage.googleapis.com/demo-ecom-backfill/ecom_bf_23_6_10M.parquet"

parquet_files=("${(@f)backfill_files}")

# loop through the rest of the files and append them to the datasource
# have to sleep at least 15s to avoid rate limiting

for i in "${parquet_files[@]}"; do
    curl \
    -H "Authorization: Bearer ${TB_TOKEN}" \
    -X POST "https://${TB_HOST}/v0/datasources?name=${DATA_SOURCE_NAME}&mode=append&format=parquet" \
    -d url="$i"
    sleep 40
done