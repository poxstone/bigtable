# BIGTABLE

>[https://cloud.google.com/bigtable/docs/samples-python-hello](https://cloud.google.com/bigtable/docs/samples-python-hello)
>[https://cloud.google.com/bigtable/docs/quickstart-cbt](https://cloud.google.com/bigtable/docs/quickstart-cbt)

## Variables

```bash
export PROJECT_ID="my-gcp-project";
export BT_INSTANCE="bt-instance";
export BT_ZONE="us-central1-c";
export BT_TABLE="bt-table01";
export BT_COLUM_FAMILY="bt-familycol1";
export BT_COLUM_A="my_column_a";
```

## Create instance

- Create Bigtable instance
```bash
gcloud bigtable instances create "${BT_INSTANCE}" --display-name="${BT_INSTANCE}" --project="${PROJECT_ID}" --cluster-storage-type="HDD" --cluster-config="id=${BT_INSTANCE}-a,zone=${BT_ZONE},nodes=1";
```

- Create config connection
```bash
echo "
project = ${PROJECT_ID}
instance = ${BT_INSTANCE}
" > ~/.cbtrc;
```

## cbt Edit instance

> **Documentation:** [cbt-reference](https://cloud.google.com/bigtable/docs/cbt-reference)

- List instances
```bash
cbt listinstances;
```
- Create table and family column
```bash
# create schema
cbt createtable  "${BT_TABLE}";
cbt createfamily "${BT_TABLE}" "${BT_COLUM_FAMILY}";
```
- List tables and column family
```bash
# list tables
cbt ls;
cbt ls "${BT_TABLE}";
```
- Add row registries
```bash
# add registry 1
cbt set "${BT_TABLE}" "rowkey#a#1" "${BT_COLUM_FAMILY}:${BT_COLUM_A}=test1-value-1a";

# read table
cbt read "${BT_TABLE}";

# add registry 1 version 2
cbt set "${BT_TABLE}" "rowkey#a#1" "${BT_COLUM_FAMILY}:${BT_COLUM_A}=test1-value-1b";

# read table
cbt read "${BT_TABLE}";

# add registry 2
cbt set "${BT_TABLE}" "rowkey#b#1" "${BT_COLUM_FAMILY}:${BT_COLUM_A}=test2-value-1a";

# read table
cbt read "${BT_TABLE}";
```
- Search registries and export to txt (type startwith)
```bash
cbt read "${BT_TABLE}=rowkey#" > "bt_output.txt";  # ctrl + c for stop
```
- Set Max versions column Family (better add parameeter in registry insert, see mai.py)
```bash
cbt setgcpolicy "${BT_TABLE}" "${BT_COLUM_FAMILY}" maxversions="1";
```
- Delete row registry exactly
```bash
cbt deleterow ${BT_TABLE} "rowkey#a#1";
```
- Conut rows table
```bash
cbt count "${BT_TABLE}";
```
- Delete table
```bash
cbt deletetable "${BT_TABLE}";
```

## Python3

```bash
python3 -m virtualenv venv;
source venv/bin/activate;

pip install -r requirements.txt;

python main.py;
```

## Bigquery federation table

```bash
export PROJECT_ID="my-gcp-project";
export BQ_DATASET="ds_federation_bq";
export BQ_LOCATION="US";
export BQ_TABLE="bt-table01";
```

```bash
bq --location="US" mk -d "${PROJECT_ID}:${BQ_DATASET}";
```

```bash
bq query --use_legacy_sql=false "${PROJECT_ID}:${BQ_DATASET}";
```

```bash
echo "
CREATE OR REPLACE EXTERNAL TABLE \`${PROJECT_ID}.${BQ_DATASET}.${BQ_TABLE}\` OPTIONS( 
  format='CLOUD_BIGTABLE',
  uris=['https://googleapis.com/bigtable/projects/${PROJECT_ID}/instances/${BT_INSTANCE}/tables/${BT_TABLE}'],
  bigtable_options='{\"readRowkeyAsString\":\"true\",\"columnFamilies\":[{\"familyId\":\"${BT_COLUM_FAMILY}\",\"type\":\"STRING\",\"encoding\":\"TEXT\",\"columns\":[{\"qualifierString\":\"${BT_COLUM_A}\",\"type\":\"STRING\",\"encoding\":\"TEXT\"}]}]}'
  )
" > table_federation.sql;
# send to bq
bq query --use_legacy_sql=false < table_federation.sql;
```
