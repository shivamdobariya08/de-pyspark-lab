terraform {
  required_version = ">= 1.17.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "ap-southeast-2"
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Program     = "de-lab"
      Environment = "dev"
      ManagedBy   = "Terraform"
    }
  }
}

resource "random_id" "bucket" {
  byte_length = 4
}

resource "aws_s3_bucket" "parquet" {
  bucket        = "de-lab-dev-parquet-${random_id.bucket.hex}"
  force_destroy = false
}

resource "aws_s3_bucket_public_access_block" "parquet" {
  bucket = aws_s3_bucket.parquet.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "parquet" {
  bucket = aws_s3_bucket.parquet.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "parquet" {
  bucket = aws_s3_bucket.parquet.id

  versioning_configuration {
    status = "Enabled"
  }
}

output "bucket_name" {
  value = aws_s3_bucket.parquet.bucket
}

output "bucket_region" {
  value = var.aws_region
}
