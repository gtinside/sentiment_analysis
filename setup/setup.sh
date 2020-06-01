#!/bin/bash
# Script for setting up the project locally for development
# 1. Create a network - sentimental_network
# 2. Install and start localstack https://github.com/localstack/localstack
# 3. Install and install redis

# Create a new network sentimental_network
docker network create sentimental_network
docker network list

# Configure redis locally for development
docker-compose create
docker-compose restart