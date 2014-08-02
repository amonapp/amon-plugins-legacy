test_mongo:
	cp mongo/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile


test_redisdb:
	cp redisdb/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile