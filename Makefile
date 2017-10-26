test:
	coverage run --source='.' manage.py test
test_coverage: test
	coverage html
lint:
	prospector --profile .prospector_profile.yaml

