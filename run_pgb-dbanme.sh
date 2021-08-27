#!/bin/bash

RUN_DATE=`date --date="1 days ago" +'%Y-%m-%d'`
DB_INSTANCE='instance-name' #like db-ecs-env etc
BUCKET_NAME='my-bucket-name' # FQDN name of bucket like pgbadger-db.name.com
ENV=`stg` #ENV will also be the folder (key) name in S3

echo "   "
echo "STARTING .............................................."

echo "Donwloading and combining RDS Logs for: " $RUN_DATE

python3 /home/ec2-user/rds_download_dailylog.py us-east-1 $DB_INSTANCE error/postgresql.log.$RUN_DATE /home/ec2-user/rds_logs/$DB_INSTANCE/$DB_INSTANCE.log.$RUN_DATE-daily

echo "pgBadger Processing ..................................."
echo "Starting pgBadger report generation for: " $RUN_DATE
#### Pay attention to -j, -U and --exclude-client, these are examples only!  if you have 8 CPU you can use -j 8
pgbadger -f rds -s 5 -t 100 -I /home/ec2-user/rds_logs/$DB_INSTANCE/$DB_INSTANCE.log.$RUN_DATE-daily -O /home/ec2-user/pgbadger_reports/$DB_INSTANCE/binary/ -H/home/ec2-user/pgbadger_reports/$DB_INSTANCE/html/ -j 8 -U pgwatch2 --exclude-client 172.31.53.34

echo "copying html files to S3..."
aws s3 sync /home/ec2-user/pgbadger_reports/$DB_INSTANCE/html/. s3://$BUCKET_NAME/$ENV/

echo "FINISHED"
echo "-------------------------------------"