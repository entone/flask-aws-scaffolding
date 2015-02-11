provider "aws" {
    access_key = "${var.aws_access_key}"
    secret_key = "${var.aws_secret_key}"
    region = "${var.aws_region}"
}

module "vpc" {
    source = "github.com/entone/terraform-aws-vpc"
    network = "10.0"
    aws_key_name = "devops"
    aws_access_key = "${var.aws_access_key}"
    aws_secret_key = "${var.aws_secret_key}"
    aws_region = "${var.aws_region}"
    aws_key_path = "${var.aws_key_path}"
}

resource "aws_elb" "web" {
    name = "app-elb"

    subnets = [
        "${module.vpc.bastion_subnet}",
    ]

    listener {
        instance_port = 80
        instance_protocol = "http"
        lb_port = 80
        lb_protocol = "http"
    }

    health_check {
        healthy_threshold = 2
        unhealthy_threshold = 2
        timeout = 3
        target = "HTTP:80/healthcheck"
        interval = 30
    }

    security_groups = [
        "${aws_security_group.web.id}"
    ]

    instances = ["${aws_instance.app.id}"]
}

resource "aws_instance" "app" {
    ami = "${lookup(var.amis, var.aws_region)}"
    instance_type = "t2.medium"
    key_name = "devops"
    subnet_id = "${module.vpc.aws_subnet_app_id}"
    connection {
        # The default username for our AMI
        user = "ubuntu"

        # The path to your keyfile
        key_file = "${var.aws_key_path}"
    }

    user_data = "${file(\"./user_data.yml\")}"

    security_groups = [
        "${aws_security_group.app.id}",
    ]
}

resource "aws_security_group" "app" {
    name = "app"
    description = "Allows ssh and elb connections to app nodes"
    vpc_id = "${module.vpc.aws_vpc_id}"

    # HTTP access from anywhere
    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "web" {
    name = "app_public"
    description = "Allows all requests to ELB on port 80"
    vpc_id = "${module.vpc.aws_vpc_id}"

    # HTTP access from anywhere
    ingress {
        from_port = 80
        to_port = 80
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}
