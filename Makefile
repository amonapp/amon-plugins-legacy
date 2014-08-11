cleanup:
	rm -f Dockerfile

test_mongo: cleanup
	cp mongo/Dockerfile Dockerfile
	docker build --rm=true .
	rm Dockerfile


test_redisdb: cleanup
	cp redisdb/Dockerfile Dockerfile
	docker build --rm=true .
	rm Dockerfile


test_postgres: cleanup
	cp postgres/Dockerfile Dockerfile
	docker build --rm=true .
	rm Dockerfile

# Build the base container -> amonbase
init: cleanup
	docker pull phusion/baseimage
	cp Dockerfile.init Dockerfile
	docker build -t amonbase . 