# ===========================================================
# SIDMS Infrastructure as Code - Terraform Configuration
# AWS Resources for Production Deployment
# ===========================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    mongodb = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.0"
    }
  }
}

# Configure AWS Provider
provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "SIDMS"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Configure MongoDB Atlas Provider
provider "mongodb" {
  public_key  = var.mongodb_public_key
  private_key = var.mongodb_private_key
}

# ===========================================================
# Variables
# ===========================================================
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "mongodb_public_key" {
  description = "MongoDB Atlas Public Key"
  type        = string
  sensitive   = true
}

variable "mongodb_private_key" {
  description = "MongoDB Atlas Private Key"
  type        = string
  sensitive   = true
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "sidms.com"
}

# ===========================================================
# MongoDB Atlas Resources
# ===========================================================

# MongoDB Atlas Project
resource "mongodbatlas_project" "sidms" {
  name   = "SIDMS-${var.environment}"
  org_id = var.mongodb_org_id
}

# MongoDB Atlas Cluster
resource "mongodbatlas_cluster" "sidms" {
  project_id   = mongodbatlas_project.sidms.id
  name         = "sidms-cluster-${var.environment}"
  
  cluster_type = "REPLICASET"
  
  provider_name = "TENANT"
  provider_settings {
    provider_name     = "TENANT"
    backing_provider_name = "AWS"
    region_name      = var.aws_region
  }
  
  instance_size_name = var.environment == "prod" ? "M30" : "M10"
  
  auto_scaling {
    disk_gb_enabled = true
    compute {
      enabled          = true
      scale_down_enabled = true
      min_instance_size_name = "M10"
      max_instance_size_name = "M30"
    }
  }
  
  backup_enabled = var.environment == "prod" ? true : false
  
  depends_on = [mongodbatlas_project.sidms]
}

# MongoDB Atlas Database User
resource "mongodbatlas_database_user" "sidms_app" {
  username           = "sidms-app-user"
  password           = random_password.db_user_password.result
  auth_database_name = "admin"
  project_id        = mongodbatlas_project.sidms.id
  
  roles {
    role_name     = "readWrite"
    database_name = "sidms_${var.environment}"
  }
}

# Random password for database user
resource "random_password" "db_user_password" {
  length  = 32
  special = true
}

# MongoDB Atlas IP Access
resource "mongodbatlas_project_ip_access_list" "cidr" {
  project_id = mongodbatlas_project.sidms.id
  cidr_block = "0.0.0.0/0"  # Restrict in production
  comment    = "Access from anywhere"
}

# ===========================================================
# AWS S3 Resources
# ===========================================================

# S3 Bucket for file storage
resource "aws_s3_bucket" "sidms_files" {
  bucket = "sidms-files-${var.environment}-${random_id.bucket_suffix.result}"
  
  tags = {
    Name        = "SIDMS Files Bucket"
    Environment = var.environment
  }
}

# Random suffix for bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "sidms_files" {
  bucket = aws_s3_bucket.sidms_files.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "sidms_files" {
  bucket = aws_s3_bucket.sidms_files.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "sidms_files" {
  bucket = aws_s3_bucket.sidms_files.id
  
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ===========================================================
# AWS ECS Resources
# ===========================================================

# VPC
resource "aws_vpc" "sidms" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = {
    Name = "SIDMS-VPC-${var.environment}"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.sidms.id
  cidr_block        = "10.0.${count.index + 1}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "SIDMS-Public-Subnet-${count.index + 1}-${var.environment}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.sidms.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  
  tags = {
    Name = "SIDMS-Private-Subnet-${count.index + 1}-${var.environment}"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "sidms" {
  vpc_id = aws_vpc.sidms.id
  
  tags = {
    Name = "SIDMS-IGW-${var.environment}"
  }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.sidms.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.sidms.id
  }
  
  tags = {
    Name = "SIDMS-Public-RT-${var.environment}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# ECS Cluster
resource "aws_ecs_cluster" "sidms" {
  name = "sidms-${var.environment}"
  
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  
  tags = {
    Name = "SIDMS-ECS-${var.environment}"
  }
}

# Task Definition
resource "aws_ecs_task_definition" "sidms" {
  family                   = "sidms-${var.environment}"
  network_mode             = "awsvpc"
  requires_compatibilities    = ["FARGATE"]
  cpu                      = var.environment == "prod" ? "1024" : "512"
  memory                   = var.environment == "prod" ? "2048" : "1024"
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn           = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([
    {
      name  = "sidms-backend"
      image = "${aws_ecr_repository.sidms.repository_url}:latest"
      
      environment = [
        {
          name  = "SPRING_PROFILES_ACTIVE"
          value = var.environment
        },
        {
          name  = "MONGODB_ATLAS_URI"
          value = "mongodb+srv://${mongodbatlas_database_user.sidms_app.username}:${random_password.db_user_password.result}@${mongodbatlas_cluster.sidms.connection_strings[0].standard_srv}/sidms_${var.environment}?retryWrites=true&w=majority&ssl=true"
        },
        {
          name  = "AWS_S3_BUCKET"
          value = aws_s3_bucket.sidms_files.bucket
        }
      ]
      
      secrets = [
        {
          name      = "SIDMS_MAIL_USERNAME"
          valueFrom = aws_secretsmanager_secret.mail_credentials.arn
        },
        {
          name      = "SIDMS_MAIL_PASSWORD"
          valueFrom = aws_secretsmanager_secret.mail_credentials.arn
        },
        {
          name      = "SIDMS_AES_KEY"
          valueFrom = aws_secretsmanager_secret.encryption_key.arn
        },
        {
          name      = "AWS_ACCESS_KEY"
          valueFrom = aws_secretsmanager_secret.aws_credentials.arn
        },
        {
          name      = "AWS_SECRET_KEY"
          valueFrom = aws_secretsmanager_secret.aws_credentials.arn
        }
      ]
      
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]
      
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/sidms-${var.environment}"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
  
  tags = {
    Name = "SIDMS-Task-${var.environment}"
  }
}

# ECS Service
resource "aws_ecs_service" "sidms" {
  name            = "sidms-backend"
  cluster         = aws_ecs_cluster.sidms.id
  task_definition = aws_ecs_task_definition.sidms.arn
  desired_count   = var.environment == "prod" ? 3 : 1
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups   = [aws_security_group.sidms.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.sidms.arn
    container_name   = "sidms-backend"
    container_port   = 8080
  }
  
  depends_on = [aws_lb_listener.sidms]
  
  tags = {
    Name = "SIDMS-Service-${var.environment}"
  }
}

# ===========================================================
# AWS Security and IAM
# ===========================================================

# Security Group
resource "aws_security_group" "sidms" {
  name_prefix = "sidms-"
  vpc_id      = aws_vpc.sidms.id
  
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
  
  tags = {
    Name = "SIDMS-SG-${var.environment}"
  }
}

# ECS Execution Role
resource "aws_iam_role" "ecs_execution" {
  name = "sidms-ecs-execution-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ECS Task Role
resource "aws_iam_role" "ecs_task" {
  name = "sidms-ecs-task-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

# ===========================================================
# AWS Load Balancer
# ===========================================================

# Application Load Balancer
resource "aws_lb" "sidms" {
  name               = "sidms-alb-${var.environment}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.sidms.id]
  subnets           = aws_subnet.public[*].id
  
  enable_deletion_protection = var.environment == "prod" ? true : false
  
  tags = {
    Name = "SIDMS-ALB-${var.environment}"
  }
}

# Target Group
resource "aws_lb_target_group" "sidms" {
  name     = "sidms-tg-${var.environment}"
  port     = 8080
  protocol = "HTTP"
  vpc_id   = aws_vpc.sidms.id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval          = 30
    matcher           = "200"
    path              = "/actuator/health"
    port              = "traffic-port"
    protocol          = "HTTP"
    timeout           = 5
    unhealthy_threshold = 2
  }
  
  tags = {
    Name = "SIDMS-TG-${var.environment}"
  }
}

# Listener
resource "aws_lb_listener" "sidms" {
  load_balancer_arn = aws_lb.sidms.arn
  port              = "443"
  protocol          = "HTTPS"
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.sidms.arn
  }
  
  certificate_arn = aws_acm_certificate.sidms.arn
}

# ===========================================================
# AWS Certificate Manager
# ===========================================================

# SSL Certificate
resource "aws_acm_certificate" "sidms" {
  domain_name       = var.domain_name
  validation_method = "DNS"
  
  tags = {
    Name = "SIDMS-Cert-${var.environment}"
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# ===========================================================
# AWS Secrets Manager
# ===========================================================

# Mail Credentials
resource "aws_secretsmanager_secret" "mail_credentials" {
  name = "sidms/mail-credentials-${var.environment}"
  
  tags = {
    Name = "SIDMS-Mail-${var.environment}"
  }
}

# Encryption Key
resource "aws_secretsmanager_secret" "encryption_key" {
  name = "sidms/encryption-key-${var.environment}"
  
  tags = {
    Name = "SIDMS-Encryption-${var.environment}"
  }
}

# AWS Credentials
resource "aws_secretsmanager_secret" "aws_credentials" {
  name = "sidms/aws-credentials-${var.environment}"
  
  tags = {
    Name = "SIDMS-AWS-${var.environment}"
  }
}

# ===========================================================
# Data Sources
# ===========================================================

data "aws_availability_zones" "available" {
  state = "available"
}

# ===========================================================
# Outputs
# ===========================================================
output "mongodb_connection_string" {
  description = "MongoDB Atlas connection string"
  value       = "mongodb+srv://${mongodbatlas_database_user.sidms_app.username}:${random_password.db_user_password.result}@${mongodbatlas_cluster.sidms.connection_strings[0].standard_srv}/sidms_${var.environment}?retryWrites=true&w=majority&ssl=true"
  sensitive   = true
}

output "s3_bucket_name" {
  description = "S3 bucket name for file storage"
  value       = aws_s3_bucket.sidms_files.bucket
}

output "load_balancer_dns" {
  description = "Load balancer DNS name"
  value       = aws_lb.sidms.dns_name
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.sidms.name
}

output "database_password" {
  description = "Database user password"
  value       = random_password.db_user_password.result
  sensitive   = true
}
