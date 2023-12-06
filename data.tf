data "aws_lambda_function" "cloudwatch_lambda" {
    function_name = var.cloudwatch_alerts
}

data "aws_lambda_function" "backend_lambda" {
  function_name = var.lambda_integration
}

data "aws_lambda_function" "auth_lambda" {
  function_name = var.lambda_authorizer
}