# delete aws cloudwatch empty LogStream
not LogGroup.

## not lambda(role). exec in local.
```
cp -p .env.example .env
```

and write iam credencials.

exec
```
docker run --rm --env-file ./.env -v "$PWD":/var/task lambci/lambda:python3.8 lambda_function.lambda_handler
```

```
docker run --rm --env-file ./.env -v "$PWD":/var/task lambci/lambda:python3.8 lambda_function.lambda_handler | jq -r '.'
```

### set log retention
days: `1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653`

```
aws logs put-retention-policy --log-group-name /aws/rds/instance/mysqlhoge/error --retention-in-days 30
```
