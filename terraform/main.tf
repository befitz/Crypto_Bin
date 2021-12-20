resource "aws_iam_role" "crypto_trading_bot_execution_role" {
  name = "crypto_trading_bot_execution_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_lambda_function" "crypto_trading_bot" {
  function_name               = "use1_crypto_trading_bot"
  role                        = aws_iam_role.crypto_trading_bot_execution_role.arn
  handler                     = var.lambda_handler
  runtime                     = "python3.8"
  memory_size                 = 128
  timeout                     = 10 # seconds

  tracing_config {
    mode = "Active"
  }

  environment {
    variables = {

    }
  }

  vpc_config {
    security_group_ids        = [var.ecs_service_security_group]
    subnet_ids                = var.core_info.private_subnets
  }

}

resource "aws_cloudwatch_event_rule" "crypto_trading_bot_event_rule" {
  name                = "crypto_trading_bot_event_rule"
  description         = "Triggers an event every 2 hours, starting at midnight UTC"

  schedule_expression = "cron(0 0/2 ? * * *)"
}

# Connects the Event and the Trading Bot together.
# Allows the lambda to execute when the event is triggered.
resource "aws_cloudwatch_event_target" "firebird_sync_lambda_target" {
  rule      = aws_cloudwatch_event_rule.crypto_trading_bot_event_rule.name

  target_id = aws_lambda_function.crypto_trading_bot.id
  arn       = aws_lambda_function.crypto_trading_bot.arn

  input     = ""
}
