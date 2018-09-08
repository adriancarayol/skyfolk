#!/bin/sh
# STOP NEO4J, RABBITMQ, REDIS, POSTGRESQL AND ELASTICSEARCH ON LOCALHOST

echo "Stopping elasticsearch..."
sudo systemctl stop elasticsearch
if [ $? -eq 0 ]
then
    echo "Elasticsearch stopped"
fi
echo "Stopping neo4j..."
sudo systemctl stop neo4j
if [ $? -eq 0 ]
then
    echo "Neo4j stopped"
fi
echo "Stopping rabbitmq-server"
sudo systemctl stop rabbitmq-server
if [ $? -eq 0 ]
then
    echo "Rabbitmq-Server stopped"
fi
echo "Stopping redis server..."
sudo systemctl stop redis-server
if [ $? -eq 0 ]
then
    echo "Redis-server stopped"
fi
echo "Stopping postgresql..."
sudo systemctl stop postgresql
if [ $? -eq 0 ]
then
    echo "PostgreSQL stopped"
fi
