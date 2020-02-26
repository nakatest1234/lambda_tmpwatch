import boto3
import time
import os

def day2timestamp(days):
	return int((time.time() - (days * 24 * 3600))*1000) # ms

def lambda_handler(event, context):
	# 対象ログストリームのlastEventTimestampの対象フィルタ検索の日数を遅らせる
	delay_days = int(os.environ.get('DELAY_DAYS', 14))
	dryrun     = int(os.environ.get('dryrun', 0))

	client = boto3.client('logs')

	# retentionInDaysを持つロググループが対象
	log_groups = list(filter(lambda x: 'retentionInDays' in x, client.describe_log_groups()['logGroups']))

	# 削除arn
	delete_arns = []

	# ロググループを回す
	for group in log_groups:
		logGroupName = group['logGroupName']
		log_streams = client.describe_log_streams(
				logGroupName=logGroupName,
				orderBy='LastEventTime',
				descending=False,
		)['logStreams']

		# 指定日数多め + サイズ0でフィルタ
		targetTimestamp = day2timestamp(group['retentionInDays']+delay_days)
		tmp = list(filter(lambda x: x['storedBytes']==0 and 'lastEventTimestamp'in x and x['lastEventTimestamp']<targetTimestamp, log_streams))

		for logStream in tmp:
			# 削除対象
			delete_arns.append(logStream['arn'])

			if (dryrun==0):
				client.delete_log_stream(
					logGroupName=logGroupName,
					logStreamName=logStream['logStreamName'],
				)

	return {
		'dryrun': dryrun,
		'deleted':delete_arns,
	}
