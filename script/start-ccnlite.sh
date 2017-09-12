#!/bin/sh

mode=${mode:-sics}

case ${mode} in
    sics)
	#PI2_IP4=${PI2_IP4:-193.10.67.23}
	PI2_IP4=${PI2_IP4:-193.10.67.8}
	;;
    demo)
	PI2_IP4=${PI2_IP4:-192.168.42.104}
	;;
esac

#M1_IP6=${M1_IP6:-fd02::212:4b00:7a8:7185}
M1_IP6=${M1_IP6:-fd02::212:4b00:7a8:2883}

# these are ccn-lite default ports for ccnx2015 encoding
# but we are for now abusing them with ndn2013 encoding...
RELAYPORT=${RELAYPORT:-9995}
WWWPORT=${WWWPORT:-9995}
SUITE=${SUITE:-ndn2013}

SOCK=${SOCK:-/tmp/mgmt-relay-gw.sock}
CCNL_PATH=${CCNL_PATH:-/home/johanc/ccn-lite/bin}
LOG=${LOG:-/home/johanc/log/ccnl-relay.log}
DEBUG_LEVEL=${DEBUG_LEVEL:-debug}
MAX_CONTENT_ENTRIES=${MAX_CONTENT_ENTRIES:-0}
PREFIX=${PREFIX:-smote1mote2mote3mote4mote5mote6}
#PREFIX=${PREFIX:-/sens/tes/tes/tes/tes/tes/tes/tes}

if [ -e "${LOG}" ]; then
    mv ${LOG} ${LOG}.old
fi

# TESTING Start CCN-lite relay in the background with output to log file
#${CCNL_PATH}/ccn-lite-relay -s ${SUITE} -c ${MAX_CONTENT_ENTRIES} -t ${WWWPORT} -x ${SOCK} -u ${RELAYPORT} -6 $((${RELAYPORT}+1)) > ${LOG} 2>&1 &

# Start CCN-lite relay in the background with output to log file
${CCNL_PATH}/ccn-lite-relay -v ${DEBUG_LEVEL} -s ${SUITE} -c ${MAX_CONTENT_ENTRIES} -t ${WWWPORT} -x ${SOCK} -u ${RELAYPORT} -6 $((${RELAYPORT}+1)) > ${LOG} 2>&1 &

sleep 1

# Configure face and route towards mote1 working
#FACEID=`${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} newUDP6face any ${M1_IP6} 1001 | ${CCNL_PATH}/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/'`
#${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} prefixreg /demo/mote1 ${FACEID} ndn2013 | ${CCNL_PATH}/ccn-lite-ccnb2xml | grep ACTION

# TESTING
FACEID=`${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} newUDP6face any ${M1_IP6} 1001 | ${CCNL_PATH}/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/'`
${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} prefixreg ${PREFIX} ${FACEID} ndn2013 | ${CCNL_PATH}/ccn-lite-ccnb2xml | grep ACTION

# Configure face and route towards CCN-lite relay on icnpi2 with mote2
#FACEID=`${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} newUDPface any ${PI2_IP4} ${RELAYPORT} | ${CCNL_PATH}/ccn-lite-ccnb2xml | grep FACEID | sed -e 's/^[^0-9]*\([0-9]\+\).*/\1/'`
#${CCNL_PATH}/ccn-lite-ctrl -x ${SOCK} prefixreg /demo/mote2 ${FACEID} ndn2013 | ${CCNL_PATH}/ccn-lite-ccnb2xml| grep ACTION
