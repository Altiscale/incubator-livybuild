#!/bin/bash

# TBD: honor system pre-defined property/variable files from 
# /etc/hadoop/ and other /etc config for spark, hdfs, hadoop, etc


curr_dir=`dirname $0`
curr_dir=`cd $curr_dir; pwd`

export JAVA_HOME=${JAVA_HOME:-"/usr/java/default"}
export ANT_HOME=${ANT_HOME:-"/opt/apache-ant"}
export MAVEN_HOME=${MAVEN_HOME:-"/usr/share/apache-maven"}
export M2_HOME=${M2_HOME:-"/usr/share/apache-maven"}
export SCALA_HOME=${SCALA_HOME:-"/opt/scala"}
export SCALA_VERSION=${SCALA_VERSION:-"2.11"}
export HADOOP_VERSION=${HADOOP_VERSION:-"2.7.4"}
# Spark 1.5+ default Hive starts with 1.2.1, backward compatible with Hive 1.2.0
export SPARK_VERSION=${SPARK_VERSION:-"2.2.1"}

export PATH=$PATH:$M2_HOME/bin:$SCALA_HOME/bin:$ANT_HOME/bin:$JAVA_HOME/bin

# Honor incubator-livy-pkg-env.sh env varibales and value
export PACKAGE_NAME=${PACKAGES:-"incubator-livy"}
export LIVY_VERSION=${LIVY_VERSION:-"0.4.0"}
export MAVEN_OPTS=${MAVEN_OPTS:-"-Xmx2048m -XX:MaxPermSize=1024m"}

# centos6.5-x86_64
# centos6.6-x86_64
# centos6.7-x86_64
export BUILD_TIME=$(date +%Y%m%d%H%M)
# Customize build OPTS for MVN

workspace_dir=$curr_dir
export WORKSPACE=${WORKSPACE:-$workspace_dir}
