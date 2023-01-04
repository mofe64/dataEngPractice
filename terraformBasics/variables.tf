locals {
  data_lake_bucket = "first_data_lake"
}

variable "project" {
  description = "gcp project id"
}

variable "region" {
  description = "Region for gcp resources"
  default = "europe-west6"
  type = string
}

variable "storage_class" {
  description = "Storage class type for your bucket"
  default = "STANDARD"
}

variable "BQ_DATASET" {
  description = "BigQueryDataset that raw data from GCS will be written to"
  type = string
  default = "trips_data_all"
}