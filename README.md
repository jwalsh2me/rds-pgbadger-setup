# rds-pgbadger-setup

Get pgBadger from: [Github Repo](https://github.com/darold/pgbadger)

Assumptions:

- pgBadger is cloned and `pgbadger` binary is dropped into `/usr/local/bin` and in the path
- Amazon Linux 2 EC2 instance is being used and just using the default user.  No need for SSH, just attach the SSM policy so you can use Connection Manager to connect in.
- The -j option needs to match CPU count. This is 8, you can do 2 as long as a `t3.medium` is used
- `$DB_INSTANCE` is your AWS RDS Instance name like my-database

- File structure needed, you will need to have these directories created:

  - `mkdir ~/rds_logs/$DB_INSTANCE`
  - `mkdir ~/pgbadger_reports`
  - `mkdir ~/pgbadger_reports/$DB_INSTANCE`
  - `mkdir ~/pgbadger_reports/$DB_INSTANCE/binary`
  - `mkdir ~/pgbadger_reports/$DB_INSTANCE/html`

- You will have a S3 bucket created with Web Hosting enabled but IP restricted, URL will need to match bucketname.
- You will have an EC2 AWS Role attached with policies to allow reading logs from RDS and Writing to your new S3 bucket


The scripts:

- `rds_download_dailylogs.py` was provided as an example from AWS and was slighlty modified.  Most important is no need for access keys if you use a policy on the instance.
- `run_pgb-dbname.sh` Is the file to go grab the logs and run pgBadger on it.  You can cron it daily.  You will need to pay attention since pgBadger creates a lock file in `/tmp` while running only once instance of it can run at a time.  You will need to stagger your jobs, the sweet spot seems to me a M5 instance with 8 CPUs, but a t3.medium will work fine, just make sure `-j 2` is passed!

