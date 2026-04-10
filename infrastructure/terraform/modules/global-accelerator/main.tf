resource "aws_globalaccelerator_accelerator" "main" {
  name            = "${var.project_name}-ga"
  ip_address_type = "IPV4"
  enabled         = true

  attributes {
    flow_logs_enabled = false
  }

  tags = { Name = "${var.project_name}-global-accelerator" }
}

resource "aws_globalaccelerator_listener" "main" {
  accelerator_arn = aws_globalaccelerator_accelerator.main.id
  protocol        = "TCP"

  port_range {
    from_port = var.listener_port_start
    to_port   = var.listener_port_end
  }
}

resource "aws_globalaccelerator_endpoint_group" "main" {
  listener_arn = aws_globalaccelerator_listener.main.id

  endpoint_configuration {
    endpoint_id = var.alb_arn
    weight      = 100
  }

  health_check_port             = 80
  health_check_protocol         = "HTTP"
  health_check_path             = "/health"
  health_check_interval_seconds = 10
  threshold_count               = 3
}

variable "project_name" { type = string }
variable "alb_arn" { type = string }
variable "listener_port_start" { type = number }
variable "listener_port_end" { type = number }

output "accelerator_dns_name" {
  value = aws_globalaccelerator_accelerator.main.dns_name
}
output "accelerator_ips" {
  value = aws_globalaccelerator_accelerator.main.ip_sets[*].ip_addresses
}
