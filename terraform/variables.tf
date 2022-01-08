variable "lambda_basic_execution_role" {
    default = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

variable "binance_api_key" {
    type = string 
    description = "the api key for accessing binance REST API"
}

variable "binance_api_secret" {
    type = string 
    description = "the secret key for accessing binance REST API account operations"
}