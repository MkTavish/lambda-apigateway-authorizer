resource "aws_apigatewayv2_api" "http_api" {
  name          = "example-http-api"
  protocol_type = "HTTP"
  description   = "Example HTTP API Gateway"
}

resource "aws_apigatewayv2_integration" "http_integration" {
  api_id           = aws_apigatewayv2_api.http_api.id
  integration_type = "HTTP_PROXY"
  integration_method = "GET"
  integration_uri  = "" #Use Lambda backend
}

resource "aws_apigatewayv2_route" "get_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /get"
  target    = "integrations/${aws_apigatewayv2_integration.http_integration.id}"
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

