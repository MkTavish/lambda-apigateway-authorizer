variable "aws_region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "cloudwatch_alerts" {
  type = string
}

variable "lambda_integration" {
  type = string
}

variable "lambda_authorizer" {
  type = string
}

variable "apig-lambda-policy" {
  type = string
}

variable "apigateway-lambda-auth-role" {
  type = string
}