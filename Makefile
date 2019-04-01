all: ${CONFIG}_${FUNCTION}_${MODE}.dat

#wq-sequential-test-quick:
#	work_queue_worker cclws04 9000 --single-shot
#	python3 test.py 1 2 --test_wq_sequential 
#wq-parallel-test-quick:
#	work_queue_worker cclws04 9000 --single-shot
#	python3 test.py 1 2 --test_wq_parallel


#CONFIG=condor
#FUNCTION=cpu-short
#MODE=parallel
%_${FUNCTION}_${MODE}.dat : test.py
	python3 test.py 1 2 3 4 5 6 7 8 9 10 --config $* --function ${FUNCTION} --parallelization ${MODE} -o $*_${FUNCTION}_${MODE}.png

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
