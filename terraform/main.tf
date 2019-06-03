provider "aws" {
  region = "eu-west-1"
  shared_credentials_file = "~/.aws/credentials"
  profile = "terraform-facematch"
}

resource "aws_security_group" "WebserverSG" {
  name = "WebserverSG"
  description = "Security group for webservers"
  ingress {
    from_port = 22
    to_port = 22
    protocol = "TCP"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow incoming SSH traffic from anywhere"
  }
  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    self = true
  }
}


resource "aws_instance" "web" {
  ami = "ami-0cbf7a0c36bde57c9"
  instance_type = "t2.medium"
  key_name = "aws-key-fast-ai"
  security_groups = ["WebserverSG"]
  ebs_block_device {
    device_name = "/dev/sdg"
    volume_size = 1
    delete_on_termination = false
  }
}

