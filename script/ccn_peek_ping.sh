#!/usr/bin/env bash
# USAGE : 
# [PING] [SIZE]  [NUMBER OF ITERATIONS] [EXTRA]
#
# [PEEK] [DATA] [NUMBER OF ITERATIONS]  [EXTRA]
# EXTRA means something additional to the test, it will be put on the first place in the filename.
# ping [iterations]
# 

if [ "$1" == "ping" ]; then
mode=${mode:-local}
else
mode=${mode:-peek}
fi

case ${mode} in
	local)
	IP6=${IP6:-::1}
	;;
	peek)
	IP6=${IP6:-127.0.0.1}
	;;
	mote1)
	IP6=${IP6:-193.10.67.8}	# icnpi1.sics.se
	;;
esac

PORT=${PORT:-9995}
#SENSOR_ADDRESS=${SENSOR_ADDRESS:-fd02::212:4b00:7a8:2883}
SENSOR_ADDRESS=${SENSOR_ADDRESS:-fd02::212:4b00:7a8:7185}
CCNL_PATH=${CCNL_PATH:-/home/johanc/ccn-lite/bin}
RESULT_OUTPUT=${RESULT_OUTPUT:-/home/johanc/thesis/resultat_tester/test_09_17/ping/}
#RESULT_OUTPUT=${RESULT_OUTPUT:-/home/johanc/thesis/resultat_tester/ping/test_08_13/}
#RESULT_OUTPUT=${RESULT_OUTPUT:-/home/johanc/}
SOCK=${SOCK:-/tmp/mgmt-relay-gw.sock}


CONTENT_PATH=${CONTENT_PATH:-smotel}


# PING
TYPE=$1
TIMEOUT=2
SIZE=$2
ITERATIONS=$3
EXTRA=$4


if [ -z "$ITERATIONS" ]; then
	# not set
	ITERATIONS=1
fi

if [ -z "$TIMEOUT" ]; then
	# not set
	TIMEOUT=2
fi

if [ -z "$SIZE" ]; then
	# not set
	SIZE=56
fi

if [ -z "$EXTRA" ]; then
	# not set
	FULLNAME="${TYPE}_size_${SIZE}_bytes_iterations_${ITERATIONS}"
else
	FULLNAME="${EXTRA}_type_${FULLNAME}"
fi



function pinger {
## PING


	if [ "$SIZE" -gt 0 ]; then
		#for i in {10..250}
		for i in {17..77..5}
		do
		SIZE=$i
		FULLNAME="${TYPE}_size_${SIZE}_bytes_iterations_${ITERATIONS}"
		echo "Size.... $i"
		echo "ping6 -c $ITERATIONS -W $TIMEOUT -s $SIZE -I tun0 $SENSOR_ADDRESS >> $RESULT_OUTPUT$FULLNAME"
		ping6 -c $ITERATIONS -W $TIMEOUT -s $i -I tun0 $SENSOR_ADDRESS >> $RESULT_OUTPUT$FULLNAME
		done
	else
		echo "ping6 -c $ITERATIONS -W $TIMEOUT -s 42 -I tun0 $SENSOR_ADDRESS >> $RESULT_OUTPUT$FULLNAME"
		ping6 -c $ITERATIONS -W $TIMEOUT -s 42 -I tun0 $SENSOR_ADDRESS >> $RESULT_OUTPUT$FULLNAME
	fi

}

function peeker {
	for i in {1..100}
	do
	printf "%s" "iteration $i, " >> $RESULT_OUTPUT$FULLNAME 
	#echo "${CCNL_PATH}/ccn-lite-peek -p 1 -w $TIMEOUT -s ndn2013 -x ${SOCK} $CONTENT_PATH >> $RESULT_OUTPUT$FULLNAME"
	#${CCNL_PATH}/ccn-lite-peek -p 1 -w $TIMEOUT -s ndn2013 -x ${SOCK} $CONTENT_PATH >> $RESULT_OUTPUT$FULLNAME
	#echo "${CCNL_PATH}/ccn-lite-peek -v info -w 2 -p 1 -6 1 -s ndn2013 -u $SENSOR_ADDRESS >> $RESULT_OUTPUT$FULLNAME"
	${CCNL_PATH}/ccn-lite-peek -v info -w $TIMEOUT -p 1 -6 1 -s ndn2013 -u $SENSOR_ADDRESS/1001 $CONTENT_PATH >> $RESULT_OUTPUT$FULLNAME
	sleep 1.0
	done
}


if [ "$TYPE" == "ping" ]; then
	pinger
else
	peeker
fi


