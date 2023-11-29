data "aws_lambda_function" "backend_lambda" {
  function_name = "lambda-backend"
}

data "aws_lambda_function" "auth_lambda" {
  function_name = "lambda-auth-whitelist"
}


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
  authorizer_payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /get"
  target    = "integrations/${aws_apigatewayv2_integration.http_integration.id}"
  authorizer_id = aws_apigatewayv2_authorizer.http_authorizer.id
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

