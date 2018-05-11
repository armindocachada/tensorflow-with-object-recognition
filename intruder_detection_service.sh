#!/bin/sh
#
# chkconfig: 345 99 01
#
# description: Intruder detection service that connects to a shared folder with videos
#

. /lib/lsb/init-functions

serviceName='Intruder detection service'
startup="ipython /tensorflow/models/research/object_detection/object_detection_tutorial.py"
shutdown="kill $pid"
user=root
currentUser=`id -un`
export SHUTDOWN_WAIT=30
start(){
 echo -n $"Starting $serviceName: "

# if user is different then $user we need to use sudo
if [ "$user" = "$currentUser" ]
then
   cd /tensorflow/models/research && export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim
   cd /tensorflow/models/research/object_detection && nohup $startup > /data/intruder_detection_service.out 2>&1 </dev/null &
else
sudo -u $user -s -- <<EOF
nohup $startup > /data/intruder_detection_service.out 2>&1 </dev/null &
EOF
# wait until there is a process running for our service

until [ -n "`netstat -nat | grep 8080`" ]
do
  echo -n -e "\nwaiting for jboss processes to start";
  sleep 1
done
echo "Service pid:$(service_pids)"
fi

RETVAL=$?
}
service_pid() {
    echo `ps -fe | grep $startup | grep -v grep | tr -s " "|cut -d" " -f2`
}
service_pids() {
    echo `ps -fe | grep $CATALINA_BASE | grep -v grep | tr -s " "|cut -d" " -f2`
}

stop(){
 action $"Stopping $serviceName: "
 pid=$(service_pid)
 pids=$(service_pids)
 unauth_pid=$(unauthorized_process_kill_pid)

  if [ -n "$pid" ]
  then

echo "Stopping $serviceName"

# if user is different then $user we need to use sudo
if [ "$user" = "$currentUser" ]
then
	$shutdown
else
sudo -u $user -s -- <<EOF
$shutdown
EOF
fi

    let kwait=$SHUTDOWN_WAIT
    count=0;
    until [ `ps -p $pid | grep -c $pid` = '0' ] || [ $count -gt $kwait ]
    do
      echo -n -e "\nwaiting for processes to exit";
      sleep 1
      let count=$count+1;
    done
 
    if [ $count -gt $kwait ]; then
      echo -n -e "\nkilling processes which didn't stop after $SHUTDOWN_WAIT seconds"
      kill -9 $pids
    fi
  else
    echo "$serviceName is not running"
  fi
 
  return 0
   
}

restart(){
  stop
  start
}


# See how we were called.
case "$1" in
start)
 start
 RETVAL=0
 ;;
stop)
 stop
 RETVAL=0
 ;;
status)
 pid=$(tomcat_pid)
  if [ -n "$pid" ]
  then
    echo "$serviceName is running with pid: $pid"
    RETVAL=0
  else
    echo "$serviceName is stopped"
    RETVAL=3
  fi
  ;;
restart)
 restart
 RETVAL=0
 ;;
*)
 echo $"Usage: $0 {start|stop|status|restart}"
 exit 1
esac

exit $RETVAL

