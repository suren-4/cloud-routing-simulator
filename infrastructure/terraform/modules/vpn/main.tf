data "aws_ami" "ubuntu" {
  most_recent = true
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
  owners = ["099720109477"] # Canonical
}

resource "aws_security_group" "vpn" {
  name        = "${var.project_name}-vpn-sg"
  description = "OpenVPN Security Group"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 1194
    to_port     = 1194
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_instance" "vpn" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  subnet_id     = var.subnet_id
  vpc_security_group_ids = [aws_security_group.vpn.id]

  user_data = <<-EOF
              #!/bin/bash
              export DEBIAN_FRONTEND=noninteractive
              cd /home/ubuntu
              
              apt-get update -y
              apt-get install -y iptables-persistent python3

              curl -O https://raw.githubusercontent.com/angristan/openvpn-install/master/openvpn-install.sh
              chmod +x openvpn-install.sh
              
              export AUTO_INSTALL=y
              export ENDPOINT=$(curl -s http://checkip.amazonaws.com)
              ./openvpn-install.sh
              
              # The script puts it in /root because cloud-init runs as root. Move it!
              cp /root/*.ovpn /home/ubuntu/
              
              # Provide open permissions so the web server can read it
              chmod 777 /home/ubuntu/*.ovpn
              
              # Start web server in the same directory
              python3 -m http.server 8080 &
              EOF

  tags = {
    Name = "${var.project_name}-vpn"
  }
}
