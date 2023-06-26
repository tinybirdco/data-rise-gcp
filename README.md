# data-rise-gcp

Repo for the GCP-Tinybird workshop

## Part 1: Creating the first API Endpoint

For this first part of the workshop the plan is to ingest dimensional data from BigQuery, historical data from Google Cloud Storage, and realtime data from Pub/Sub.

Then, mixing the 3 sources, we will create a dynamic API Endpoint.



### Create your account and your first Workspace

Go to [https://ui.tinybird.co/signup](https://ui.tinybird.co/signup) to log in / sign up, and create a new Workspace.

Choose your region and go for empty workspace by default, we will not be using any Starter Kits for this workshop.

### Ingest dimensional data from BigQuery

Upload the [products CSV](./aux/products.csv) file to BigQuery.

In your Tinybird Workspace, create a new BigQuery Data Source from that BigQuery table following the [Big Query connector documentation](https://www.tinybird.co/docs/ingest/bigquery).

### Ingest from GCS

Let's do this step first cause the backfill may take a bit longer.

First, let's create a Data Source from this small [parquet file](./aux/ecom_events.parquet) we have as sample. Just drag and drop the file into the Tinybird UI. You can adjust data types, Sortng Key...

Now that the data source is created, we will ingest some bigger parquets from GCS.

Copy your admin token —or a new one with append rights to your newly created _ecom_events_ data source—, edit the [backfill_gcs.sh](./aux/backfill_gcs.sh) script, and run it.

Note: for private files, or to ingest every time there are new files in the bucket, you can follow the [Ingest from GCS guide](https://www.tinybird.co/docs/guides/ingest-from-google-gcs).

### Send data from Pub/Sub

Follow the steps in the [Ingest from Pub/Sub guide](https://www.tinybird.co/docs/guides/ingest-from-google-pubsub).

Note: do not use the sample script, use [this one](./aux/pub_sub_demo.py) instead, editing lines 8,9 with your project id and topic.

```python
project_id = <YOUR_PROJECT>
topic_id = <YOUR_TOPIC_ID>
```

Note 2: do not create a Materialized View to decode the messages yet, we will do that at query time.

### Create an API Endpoint

Let's create a Pipe with several nodes:

  1. A first node to decode the messages from Pub/Sub. You'll need to use `base64()` and `JSONExtract` as shown in the [example](https://www.tinybird.co/docs/guides/ingest-from-google-pubsub.html#step-4-decode-message-data).
  1. A second node to filter only the _sale_ events and for _long sleeve_ category products querying the previous node where we decoded the Pub/Sub messages.
  1. A third node to apply the same filter to the historical data, and only the sales for today.
  1. A fourth node to make a `union all` of nodes 2 and 3, and make an aggregation —a `count()` is fine— to know the number of sales
  1. Let's enrich the ranking to show product _name_ instead of _id_ and _total_revenue_ (price * units sold)

And let's create an API Endpoint from there.

### Make it dynamic

Make the endpoint accept query params with the templating language. Check the syntax [here](https://www.tinybird.co/docs/query-parameters)

For example, let's make the `category` and `event` types dynamic, and let's document them for our frontend colleagues to know what things they can pass.

## Part 2: Some optimizations with Materialized Views

### Create a Materialized View to decode Pub/Sub messages

With [Materialized Views](https://www.tinybird.co/docs/concepts/materialized-views) we can use a Pipe and persist them in a Datasource.
Choose Sorting Key and Data Types wisely. Recommended reads after the workshop: [Best Practices for faster SQL](https://www.tinybird.co/docs/guides/best-practices-for-faster-sql) and [Thinking in Tinybird](https://www.tinybird.co/blog-posts/thinking-in-tinybird).

Compare processed data —using [Service Data Sources](https://www.tinybird.co/docs/monitoring/service-datasources) like `tinybird.pipe_stats_rt`— to see the difference between querying the MV and having to decode at query time.

## Create a MV to aggregate by time (hour, day…)

AggregatingMergeTrees 101. Check [this guide](https://www.tinybird.co/docs/guides/master-materialized-views.html#doing-aggregations-the-right-way-with-materialized-views) to learn about State and Merge modifiers.

Note that if you create the MV from the UI, Tinybird will add the `State` modifier for you, but you will still need to use `Merge` and group by at query time.

Create a MV that aggregates the sales, views, or carts per product and hour/day —tip: `toStartofHour()` and `toDate()` are your allies here—.

Compare the same queries from raw data and from Aggregated MV.


## Part 3: Data as Code with data projects and CLI

### Download the CLI and check the Data project

You have already seen in the docs some resources —Data Sources and Pipes— in text format, let's download the [CLI](https://www.tinybird.co/docs/cli) and start working with it.

```bash
tb auth

tb init

tb workspace current

tb pull --auto
```

Edit a Pipe that ends in an endpoint and send it back to the Workspace with `tb push`.

### Push some resources to feed a dashboard

Go to the branch called _chart-branch_ and copy its content —/pipes, /datasources, and /endpoints— into your data project.

```bash
git checkout chart-branch
cp -r ./data-project/pipes ./pipes
cp -r ./data-project/datasources ./datasources
cp -r ./data-project/endpoints ./endpoints
```

Push the resources.

```bash
tb push pipes/events_by_*.pipe --push-deps --populate
tb push endpoints/api_*.pipe
```

Get your _dashboard_ token, go to this [webpage](https://ecommerce-svelte-tremor-dashboard.vercel.app/), and paste it in the Token input. You can start playing with the filters, hours...

Note we are assuming that the GCS Data Source is called prods, and some types may mismatch. To see the demo fully working you can check this [repo](https://github.com/tinybirdco/ecommerce-svelte).

## Extra: what we left outside the workshop

- [Apigee](https://www.tinybird.co/docs/publish/api-gateways.html#google-cloud-apigee)
- [Kafka connector](https://www.tinybird.co/docs/ingest/kafka)
- [Snowflake connector](https://www.tinybird.co/docs/ingest/snowflake), very similar to BQ.
- [Tokens](https://www.tinybird.co/docs/concepts/auth-tokens)
- [Multitenancy](https://www.tinybird.co/blog-posts/multi-tenant-saas-options), [sharing data sources between workspaces](https://www.tinybird.co/blog-posts/new-feature-sharing-data-sources-across-workspaces).
- [Copy Pipes](https://www.tinybird.co/docs/publish/copy-pipes.html)
- [Time Series](https://www.tinybird.co/blog-posts/announcing-time-series)
- Visualizing in [Grafana](https://www.tinybird.co/docs/guides/consume-api-endpoints-in-grafana) or sending data to [Datadog](https://www.tinybird.co/blog-posts/how-to-monitor-tinybird-using-datadog-with-vector-dev) using vector.dev
