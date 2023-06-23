# data-rise-gcp

Repo for the GCP-Tinybird workshop

## Part 1: Creating the first API Endpoint

For this first part of the workshop the plan is to ingest dimensional data from BigQuery, historical data from Google Cloud Storage, and realtime data from Pub/Sub.

Then, mixing the 3 sources, we will create a dynamic API Endpoint.



### Create your account and your first Workspace

Go to [https://ui.tinybird.co/signup](https://ui.tinybird.co/signup) to log in / sign up, and create a new Workspace.

Choose your region and go for empty workspace by default, we don’t want any Starter Kit for this workshop.

### Ingest dimensional data from BigQuery

Upload the [products CSV](./aux/products.csv) file to BigQuery.

In your Tinybird Workspace, create a new BigQuery Data Source from that BQ table following the [Big Query connector documentation](https://www.tinybird.co/docs/ingest/bigquery).

### Ingest from GCS

Let's do this step first cause the backfill may take a bit longer.

TBD.

### Send data from Pub/Sub

Following the steps in the [Ingest from Pub/Sub guide](https://www.tinybird.co/docs/guides/ingest-from-google-pubsub)

Note: do not use the sample script, use [this one](./aux/pub_sub_demo.py) instead, editing lines 8,9 with your project id and topic.

```python
project_id = <YOUR_PROJECT>
topic_id = <YOUR_TOPIC_ID>
```

Note 2: do not create a Materialized View to decode the messages yet, we will do that at query time.

### Create an API Endpoint

Let's create a pipe with several nodes:

  1. first node to decode the messages from Pub/Sub. You'll need to use `base64()` and `JSONExtract` as shown in the [example](https://www.tinybird.co/docs/guides/ingest-from-google-pubsub.html#step-4-decode-message-data)
  1. second node to filter only the _sale_ events and for _long sleeve_ category products querying the previous node where we decoded the Pub/Sub messages
  1. third node to apply the same filter to the historical data, and only the sales for today.
  1. fourth node to make a union all of nodes 2 and 3, and make an aggregation —a `count()` is fine— to know the number of sales
  1. let's enrich the ranking to show product _name_ instead of _id_ and _total_revenue_ (price * units sold)

And lets create an API Endpoint from there.

### Make it dynamic

Make the endpoint accept query params with the templating language. Check the syntax [here](https://www.tinybird.co/docs/query-parameters)

For example, let's make category and event type dynamic, and let's document them for our frontend colleagues to know what things they can pass.

## Part 2: Some optimizations with Materialized Views

### Create a Materialized View to decode Pub/Sub messages

With [Materialized Views](https://www.tinybird.co/docs/concepts/materialized-views) we can use a pipe and persist them in a Datasource.
Choose Sorting Key and Data Types wisely. Recommended reads after the workshop: [Best Practices for faster SQL](https://www.tinybird.co/docs/guides/best-practices-for-faster-sql) and [Thinking in Tinybird](https://www.tinybird.co/blog-posts/thinking-in-tinybird)

Compare processed data —using [Service Data Sources](https://www.tinybird.co/docs/monitoring/service-datasources) like `tinybird.pipe_stats_rt`— to see the difference between querying the MV and having to decode at query time.

## Create a MV to aggregate by time (hour, day…)

AggregatingMergeTrees 101. Check [this guide](https://www.tinybird.co/docs/guides/master-materialized-views.html#doing-aggregations-the-right-way-with-materialized-views) to learn about State and Merge modifiers.

Note that if you create the MV from the UI, Tinybird will add the `State` modifier for you, but you will still need to use `Merge` and group by at query time.

Create a MV that aggregates the sales, views, or carts per product and hour/day —tip: `toStartofHour()` and `toDate()` are your allies here—.

Compare same queries from raw data and from Aggregated MV.


## Part 3: Data as Code with data projects and CLI

### Download the CLI and check the Data project

You have already seen in the docs some resources —data sources and pipes— in text format, let's download the [CLI](https://www.tinybird.co/docs/cli) and start working with it.

```bash
tb auth

tb init

tb workspace current

tb pull --auto
```

Edit a pipe that ends in an endpoint and send it back to the Workspace with `tb push`.


## Extra: what we left outside the workshop

- [Kafka connector](https://www.tinybird.co/docs/ingest/kafka)
- [Snowflake connector](https://www.tinybird.co/docs/ingest/snowflake), very similar to BQ.
- [Tokens](https://www.tinybird.co/docs/concepts/auth-tokens)
- [Multitenancy](https://www.tinybird.co/blog-posts/multi-tenant-saas-options), [sharing data sources between workspaces](https://www.tinybird.co/blog-posts/new-feature-sharing-data-sources-across-workspaces).
- [Copy Pipes](https://www.tinybird.co/docs/publish/copy-pipes.html)
- [Time Series](https://www.tinybird.co/blog-posts/announcing-time-series)
- Visualizing in [Grafana](https://www.tinybird.co/docs/guides/consume-api-endpoints-in-grafana) or sending data to [Datadog](https://www.tinybird.co/blog-posts/how-to-monitor-tinybird-using-datadog-with-vector-dev) using vector.dev