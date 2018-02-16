#!/bin/bash -x

# This build script is only applicable to Spark without Hadoop and Hive

curr_dir=`dirname $0`
curr_dir=`cd $curr_dir; pwd`
WORKSPACE=${WORKSPACE:-"$curr_dir/workspace"}
mkdir -p $WORKSPACE
livy_git_dir=$WORKSPACE/incubator-livy
git_hash=""

if [ -f "$curr_dir/setup_env.sh" ]; then
  set -a
  source "$curr_dir/setup_env.sh"
  set +a
fi

env | sort

if [ "x${PACKAGE_BRANCH}" = "x" ] ; then
  echo "error - PACKAGE_BRANCH is not defined. Please specify the branch explicitly. Exiting!"
  exit -9
fi

echo "ok - extracting git commit label from user defined $PACKAGE_BRANCH"

pushd $WORKSPACE

pushd $livy_git_dir
git_hash=$(git rev-parse HEAD | tr -d '\n')
echo "ok - we are compiling livy branch $PACKAGE_BRANCH upto commit label $git_hash in $(pwd)"

echo "build - entire livy project in $livy_git_dir/"

if [ "x${HADOOP_VERSION}" = "x" ] ; then
  echo "fatal - HADOOP_VERSION needs to be set, can't build anything, exiting"
  exit -8
fi

echo "ok - building entire pkg with HADOOP_VERSION=$HADOOP_VERSION SPARK_VERSION=$SPARK_VERSION scala=$SCALA_VERSION"
# PURGE LOCAL CACHE for clean build
# mvn dependency:purge-local-repository

########################
# BUILD ENTIRE PACKAGE #
########################
# Default JDK version applied is 1.8 here.

spark_profile_str=""
if [[ $SPARK_VERSION == 1.* ]] ; then
  spark_profile_str="-Pspark-1.6"
elif [[ $SPARK_VERSION == 2.1.* ]] ; then
  spark_profile_str="-Pspark-2.1"
elif [[ $SPARK_VERSION == 2.2.* ]] ; then
  spark_profile_str="-Pspark-2.2"
else
  echo "fatal - Unrecognize spark version $SPARK_VERSION, can't continue, exiting, no cleanup"
  popd
	popd
	exit -9
fi

if [ "x${DEBUG_MAVEN}" = "xtrue" ] ; then
  mvn_cmd="mvn -U -X $spark_profile_str package -DskipTests"
else
  mvn_cmd="mvn -U $spark_profile_str package -DskipTests"
fi
echo "exec - $mvn_cmd"
$mvn_cmd

if [ $? -ne "0" ] ; then
  echo "fail - Livy $LIVY_VERSION build failed!"
  popd
	popd
  exit -99
fi
popd

echo "ok - build Livy $LIVY_VERSION completed successfully!"
popd

exit 0
