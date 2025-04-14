@echo off

docker rm -f analytics-container && docker rmi analytics-image

docker build -t analytics-image .

docker run -d -p 8000:8000 --name analytics-container analytics-image

