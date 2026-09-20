# AWS Serverless Job Watcher

A production serverless AWS application that automatically monitors multiple job and freelance-work sources, filters opportunities based on configurable criteria, tracks previously evaluated and reported jobs, and sends a consolidated email digest when new matching opportunities are discovered.

## Why I Built This

Traditional job boards often contain duplicate, outdated, or irrelevant postings. Checking individual employer career pages and freelance platforms manually also becomes repetitive and time-consuming.

I built AWS Serverless Job Watcher to automate that process while gaining hands-on experience designing and operating a real serverless AWS workload.

Rather than being a lab or tutorial project, the application is actively deployed in AWS and runs automatically throughout the day.

## Architecture

```text
Amazon EventBridge Scheduler
          ↓
      AWS Lambda
       (Python)
          ↓
 ┌────────┴─────────┐
 │  Job Scrapers    │
 │                  │
 │ • Appen          │
 │ • DataAnnotation │
 │ • OneForma       │
 │ • Resultant      │
 └────────┬─────────┘
          ↓
 Filtering / Eligibility Logic
          ↓
    Amazon DynamoDB
    ┌───────────────┐
    │ Evaluation    │
    │ Cache         │
    │               │
    │ Job Alert     │
    │ Deduplication │
    └───────┬───────┘
            ↓
       Amazon SNS
            ↓
       Email Digest
```

## AWS Services

- **AWS Lambda** — Executes the Python scraping and filtering application
- **Amazon EventBridge Scheduler** — Invokes the application automatically three times per day
- **Amazon DynamoDB** — Tracks previously evaluated projects and previously reported jobs
- **Amazon SNS** — Sends consolidated email notifications for new opportunities
- **Amazon CloudWatch** — Provides execution logging and monitoring
- **AWS IAM** — Provides least-privilege permissions for Lambda access to DynamoDB, SNS, and CloudWatch

## Current Job Sources

The application currently monitors multiple types of job sources:

- **Appen** — Freelance and AI-related opportunities
- **DataAnnotation** — AI training and evaluation opportunities
- **OneForma** — AI/ML evaluation, annotation, search relevance, and related freelance projects
- **Resultant** — Employer career postings through SmartRecruiters

The scraper architecture allows additional sources to be added independently.

## Filtering

Job-source-specific filtering reduces irrelevant results before notifications are generated.

Depending on the source, filters can evaluate:

- Job title
- Technical keywords
- AI/ML relevance
- Search evaluation and annotation work
- Geographic eligibility
- Language requirements
- Unwanted project categories

The goal is not to automatically decide whether a job should be pursued, but to reduce the amount of irrelevant material that requires manual review.

## Duplicate Detection

DynamoDB provides persistent state between Lambda executions.

The application maintains separate state for:

1. **Previously reported jobs** — prevents the same opportunity from generating repeated notifications.
2. **Previously evaluated OneForma projects** — prevents unchanged projects from requiring repeated detail-page requests and filtering.

This second cache was added after testing showed that evaluating OneForma projects required fetching dozens of individual project pages during each execution. Caching evaluated project URLs substantially reduced steady-state HTTP requests and Lambda execution time.

## Notifications

When new matching opportunities are discovered, the application combines them into a single SNS email digest.

Example:

```text
AWS Job Watcher - 8 New Job(s)

Online Data Labeling And Search Evaluation Tasks
https://example.com/job

Local Maps Search Evaluator
https://example.com/job
```

If no new matching jobs are discovered, no email is sent.

## Scheduling

The production Lambda function runs automatically three times per day using Amazon EventBridge Scheduler.

The schedule uses the `America/Indiana/Indianapolis` timezone so execution times remain aligned with local time.

## Authentication and IAM

The project uses environment-aware AWS authentication:

- **Local development:** AWS CLI/SSO profile
- **AWS Lambda:** IAM execution role and the AWS default credential provider chain

The Lambda execution role follows least-privilege principles and is limited to the DynamoDB tables and SNS topic required by the application.

No AWS credentials are stored in the source code.

## Project Structure

```text
AWS_serverless_job_watcher/
│
├── config/
│   └── companies.json
│
├── scrapers/
│   ├── dataannotation.py
│   ├── gig_jobs.py
│   ├── oneforma.py
│   └── smartrecruiters.py
│
├── tests/
├── utils/
│
├── main.py
├── requirements.txt
└── README.md
```

## Technologies

- Python
- AWS Lambda
- Amazon EventBridge Scheduler
- Amazon DynamoDB
- Amazon SNS
- Amazon CloudWatch
- AWS IAM
- Beautiful Soup
- Requests
- Git / GitHub

## Current Status

**Live / Production**

The application is deployed in AWS and currently:

- Runs automatically three times per day
- Monitors multiple job and freelance-work sources
- Filters opportunities for relevance
- Maintains persistent state in DynamoDB
- Prevents duplicate notifications
- Sends a single email digest when new matching opportunities are found
- Produces CloudWatch logs for monitoring and troubleshooting

## Roadmap

Completed:

- [x] Project structure and configuration
- [x] Multiple job-source scrapers
- [x] AWS Lambda deployment
- [x] Environment-aware AWS authentication
- [x] DynamoDB persistent duplicate detection
- [x] OneForma evaluation caching
- [x] SNS email notifications
- [x] EventBridge scheduled execution
- [x] CloudWatch logging
- [x] Least-privilege Lambda IAM policy

Potential future improvements:

- [ ] Additional employer and freelance sources
- [ ] Improved source-specific filtering
- [ ] Automated testing
- [ ] Infrastructure as Code
- [ ] Web dashboard
- [ ] AI-generated job summaries or relevance analysis
