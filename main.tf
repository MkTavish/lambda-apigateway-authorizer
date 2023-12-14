resource "aws_apigatewayv2_api" "http_api" {
  name          = "example-http-api"
  protocol_type = "HTTP"
  description   = "Example HTTP API Gateway"
}

resource "aws_apigatewayv2_integration" "http_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "AWS_PROXY"
  integration_method = "POST"
  integration_uri  = data.aws_lambda_function.backend_lambda.invoke_arn
}
resource "aws_apigatewayv2_authorizer" "http_authorizer" {
  api_id          = aws_apigatewayv2_api.http_api.id
  authorizer_type = "REQUEST"
  identity_sources = ["$request.header.Authorization"]
  name             = "lambda-auth-whitelist"
  authorizer_uri = data.aws_lambda_function.auth_lambda.invoke_arn
  authorizer_credentials_arn = aws_iam_role.apig_lambda_role.arn
  authorizer_payload_format_version = "2.0"
}

resource "aws_iam_role" "apig_lambda_role" {
  name = local.apigateway-auth-lambda-role
  assume_role_policy = data.aws_iam_policy_document.apig_lamnda_role_assume.json
}

resource "aws_iam_policy" "apig_lambda" {
  name = local.apig-lambda-policy
  policy = data.aws_iam_policy_document.apig_lamnda_policy.json
}

resource "aws_iam_role_policy_attachment" "apig_lambda_role_to_policy" {
  role = aws_iam_policy.apig_lambda.name
  policy_arn = aws_iam_policy.apig_lambda.arn
}

resource "aws_apigatewayv2_route" "get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /get"
  target    = "integrations/${aws_apigatewayv2_integration.http_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.http_authorizer.id
  authorization_type = "CUSTOM"
}

resource "aws_apigatewayv2_route" "get_route2" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "POST /post"
  target    = "integrations/${aws_apigatewayv2_integration.http_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.http_authorizer.id
  authorization_type = "CUSTOM"
}
resource "aws_apigatewayv2_stage" "example_stage" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "example"
  auto_deploy = true
}

resource "aws_apigatewayv2_deployment" "example_deployment" {
  api_id      = aws_apigatewayv2_api.http_api.id
  depends_on  = [aws_apigatewayv2_stage.example_stage]
}

resource "aws_sns_topic" "example_topic" {
  name = "cloudwatch-slack-topic"
}

resource "aws_sns_topic_subscription" "lambda_subscription" {
  topic_arn = aws_sns_topic.example_topic.arn
  protocol  = "lambda"
  endpoint  = data.aws_lambda_function.cloudwatch_lambda.arn
}

resource "aws_lambda_permission" "sns_invoke" {
  statement_id  = "AllowExecutionFromSNS"
  action        = "lambda:InvokeFunction"
  function_name = var.cloudwatch_alerts
  principal     = "sns.amazonaws.com"
  source_arn    = aws_sns_topic.example_topic.arn
}
