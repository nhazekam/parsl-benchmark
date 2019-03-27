quick-test: local-sequential-test-quick local-parallel-test-quick condor-sequential-test-quick condor-parallel-test-quick


local-sequential-test-quick:
	python3 test.py --num_task_list 1 --test_local_sequential


local-parallel-test-quick:
	python3 test.py --num_task_list 1 --test_local_parallel


condor-sequential-test-quick:
	python3 test.py --num_task_list 1 --test_condor_sequential


condor-parallel-test-quick:
	python3 test.py --num_task_list 1 --test_condor_parallel

condor-sequential-test-quick:
	work_queue_worker cclws04 9000 --single-shot
	python3 test.py 1 2 --test_wq_sequential 

condor-parallel-test-quick:
	work_queue_worker cclws04 9000 --single-shot
	python3 test.py 1 2 --test_wq_parallel

#SIZE=1 {1, 10, 1000} {2 4 8 16 ...} {1..10..1, 10..100..10, 100..1000..100}
#FUNCTION=quick {quick long short-sleep long-sleep small-text long-text high-volume-text}
#MODE= {seq parallel}
#CONFIG= {LOCAL CONDOR WQ}

#%_${SIZE}_${FUNCTION}_${MODE}.dat : test.py %.config ${FUNCTION}_impl.py 
#	python3 test.py --num_task_list ${SIZE} --mode ${MODE} --config $*.config --function ${FUNCTION}

#%.pdf : graph.pl %.dat
#	gnuplot -c $^
#
#
#version_% :
#	mdkir $@ && cp *.dat $@
