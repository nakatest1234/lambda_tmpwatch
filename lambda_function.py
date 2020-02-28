import boto3
import time
import os
from datetime import datetime, timedelta, timezone

myTZ = int(os.environ.get('myTZ', 9))

def datetime_jst(timestamp):
	return datetime.fromtimestamp(timestamp/1000).astimezone(timezone(timedelta(hours=myTZ))).strftime("%Y/%m/%d %H:%M:%S.%f%z")

def day2timestamp(days):
	return int((time.time() - (days * 24 * 3600))*1000) # ms

def lambda_need(v, logGroupName):
	return {
		'logGroupName': logGroupName,
		'logStreamName': v['logStreamName'],
		'lastEvent': datetime_jst(v['lastEventTimestamp'])
	}

def lambda_handler(event, context):
	# 対象ログストリームのlastEventTimestampの対象フィルタ検索の日数を遅らせる
	delay_days = int(os.environ.get('DELAY_DAYS', 14))
	dryrun     = int(os.environ.get('dryrun', 0))

	client = boto3.client('logs')

	# retentionInDaysを持つロググループが対象
	log_groups = list(filter(lambda x: 'retentionInDays' in x, client.describe_log_groups()['logGroups']))

	# 削除arn
	delete_targets = []

	# 削除対象を探す
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
		tmp2 = list(map(lambda v, logGroupName=logGroupName: lambda_need(v, logGroupName), tmp))
		delete_targets.extend(tmp2)

	# 削除実行
	if (dryrun==0):
		for target in delete_targets:
			client.delete_log_stream(
				logGroupName=target['logGroupName'],
				logStreamName=target['logStreamName'],
			)

	result = {
		'dryrun': dryrun,
		'delete_targets': delete_targets,
	}

	print(result)

	return result
