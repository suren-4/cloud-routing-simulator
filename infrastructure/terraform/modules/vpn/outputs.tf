output "vpn_public_ip" {
  description = "Public IP of the VPN server"
  value       = aws_instance.vpn.public_ip
}
