resource "aws_apigatewayv2_api" "http_api" {
  name          = "awesome-http-api"
  protocol_type = "HTTP"
  description   = "HTTP API Gateway"
}

resource "aws_apigatewayv2_stage" "http_api_stage" {
  api_id     = aws_apigatewayv2_api.http_api.id
  name       = "bastion"
  auto_deploy = true
}
