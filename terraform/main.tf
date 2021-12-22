resource "aws_iam_role" "crypto_trading_bot_role" {
  name               = "crypto_trading_bot_role"
  assume_role_policy = data.aws_iam_policy_document.basic_assume_role.json
}

resource "aws_iam_role_policy_attachment" "basic_attachment" {
  policy_arn = var.lambda_basic_execution_role
  role       = aws_iam_role.crypto_trading_bot_role.name
}

resource "aws_lambda_function" "crypto_trading_bot" {
  function_name               = "use1_crypto_trading_bot"
  filename                    = "crypto_trading_lambda.zip"
  role                        = aws_iam_role.crypto_trading_bot_role
  handler                     = "trading_event_handler"
  runtime                     = "python3.8"
  memory_size                 = 128 # smallest memory limit to save cost
  timeout                     = 10 # seconds

  environment {
    variables = {
      "X-MBX-APIKEY" = var.binance_api_key
      "X-MBX-SECURITY" = var.binance_api_secret
    }
  }
}


resource "aws_cloudwatch_event_rule" "crypto_trading_bot_event_rule" {
  name                = "crypto_trading_bot_event_rule"
  description         = "Triggers an event every 2 hours, starting at midnight UTC"

  schedule_expression = "cron(0 0/2 ? * * *)"
}


resource "aws_cloudwatch_event_target" "firebird_sync_lambda_target" {
  rule      = aws_cloudwatch_event_rule.crypto_trading_bot_event_rule.name

  target_id = aws_lambda_function.crypto_trading_bot.id
  arn       = aws_lambda_function.crypto_trading_bot.arn
}
