# AWS Serverless Job Watcher

A serverless AWS application that automatically monitors employer career pages for new IT job postings and sends email notifications when new positions match user-defined criteria.

## Why I Built This

Traditional job boards often contain duplicate, outdated, or irrelevant postings. This project automates monitoring employer career pages directly using AWS serverless services.

## Architecture

EventBridge
    ↓
AWS Lambda
    ↓
Career Page Scrapers
    ↓
DynamoDB
    ↓
SNS Email Notifications

## AWS Services

- AWS Lambda
- Amazon EventBridge
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch
- IAM

## Roadmap

- [x] Project initialized
- [ ] JSON company configuration
- [ ] First career page scraper
- [ ] Lambda deployment
- [ ] DynamoDB duplicate detection
- [ ] SNS email alerts
- [ ] Daily scheduled execution