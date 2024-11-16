Run this to build the image 

docker build --no-cache -t ragapp:v1 . 

To run the built image 

docker run -p 8000:8000 -p 11434:11434 ragapp:v1   