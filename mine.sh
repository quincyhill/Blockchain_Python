#!/bin/sh
test_value=0
while [ $test_value -le 200 ]
do
	`curl http://0.0.0.0:5000/mine`
	test_value=`expr $test_value + 1`
done
