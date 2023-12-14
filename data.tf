data "aws_lambda_function" "cloudwatch_lambda" {
    function_name = var.cloudwatch_alerts
}

data "aws_lambda_function" "backend_lambda" {
  function_name = var.lambda_integration
}

data "aws_lambda_function" "auth_lambda" {
  function_name = var.lambda_authorizer
}

data "aws_iam_policy_document" "apig_lamnda_policy" {
  statement {
    actions = [
      "lambda:InvokeFunction",
    ]
    effect = "Allow"
    resources = [data.aws_lambda_function.auth_lambda]
    sid = "ApiGatewayInvokeLambda"
  }
}

data "aws_iam_policy_document" "apig_lambda_role_assume" {
  statement {
    actions = [
      "sts:AssumeRole"
    ]
    effect = "Allow"
    principals {
      type = "Service"
      identifiers = ["apigateway.amazonaws.com"]
    }
  }
}