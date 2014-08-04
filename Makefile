cleanup:
	rm -f Dockerfile

test_mongo: cleanup
	cp mongo/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile


test_redisdb: cleanup
	cp redisdb/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile


test_postgres: cleanup
	cp postgres/Dockerfile Dockerfile
	docker build . 
	rm Dockerfile