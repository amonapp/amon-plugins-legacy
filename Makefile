test_mongo:
	cp mongo/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile