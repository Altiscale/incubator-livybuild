%define rpm_package_name      alti-livy
%define build_service_name    alti-livy
%define livy_folder_name     %{rpm_package_name}-%{_livy_version}
%define livy_testsuite_name  %{livy_folder_name}
%define install_livy_dest    /opt/%{livy_folder_name}
%define install_livy_label   /opt/%{livy_folder_name}/VERSION
%define install_livy_conf    /etc/%{livy_folder_name}
%define livy_release_dir     /opt/%{livy_folder_name}/lib

Name: %{rpm_package_name}-%{_livy_version}
Summary: %{livy_folder_name} RPM Installer AE-576, cluster mode restricted with warnings
Version: %{_livy_version}
Release: %{_altiscale_release_ver}.%{_build_release}%{?dist}
License: Apache Software License 2.0
Group: Development/Libraries
Source: %{_sourcedir}/%{build_service_name}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{release}-root-%{build_service_name}
Requires(pre): shadow-utils
# Requires: scala = 2.11.8
# BuildRequires: alti-spark-%{_spark_version}
BuildRequires: scala = 2.11.8
BuildRequires: apache-maven >= 3.3.9
BuildRequires: jdk >= 1.8.0_112

Url: http://livy.apache.org/
%description
Build from https://github.com/Altiscale/incubator-livy/tree/alti-branch-0.4 with 
build script https://github.com/Altiscale/incubator-livybuild/tree/alti-branch-0.4
Origin source form https://github.com/apache/incubator-livy/tree/branch-0.4
%{livy_folder_name} is a re-compiled and packaged livy distro that is compiled against Altiscale's 
Hadoop 2.7.x with YARN 2.7.x enabled, Spark 2.2.1, and Hive 2.1.1. This package should work with Altiscale 
Hadoop 2.7.x and Spark 2.2.1 (alti-hadoop-2.7.x and alti-spark).

%pre

%prep

%setup -q -n %{build_service_name}

%build

export JAVA_HOME=${JAVA_HOME:-"/usr/java/default"}
export MAVEN_OPTS=${MAVEN_OPTS:-"-Xmx2048m -XX:MaxPermSize=1024m"}

echo "build - entire livy project in %{_builddir}"
pushd `pwd`
cd %{_builddir}/%{build_service_name}/

if [ "x%{_hadoop_version}" = "x" ] ; then
  echo "fatal - HADOOP_VERSION needs to be set, can't build anything, exiting"
  exit -8
else
  export SPARK_HADOOP_VERSION=%{_hadoop_version}
  echo "ok - applying customized hadoop version $SPARK_HADOOP_VERSION"
fi

env | sort

echo "ok - building entire pkg with HADOOP_VERSION=$SPARK_HADOOP_VERSION SPARK_VERSION=%{_spark_version} scala=scala-%{_scala_build_version}"

# PURGE LOCAL CACHE for clean build
# mvn dependency:purge-local-repository

########################
# BUILD ENTIRE PACKAGE #
########################
# Default JDK version applied is 1.8 here.

spark_profile_str=""
if [[ %{_spark_version} == 1.* ]] ; then
  spark_profile_str="-Pspark-1.6"
elif [[ %{_spark_version} == 2.1.* ]] ; then
  spark_profile_str="-Pspark-2.1"
elif [[ %{_spark_version} == 2.2.* ]] ; then
  spark_profile_str="-Pspark-2.2"
else
  echo "fatal - Unrecognize spark version $SPARK_VERSION, can't continue, exiting, no cleanup"
  exit -9
fi

xml_setting_str=""

if [ -f %{_mvn_settings} ] ; then
  echo "ok - picking up %{_mvn_settings}"
  xml_setting_str="--settings %{_mvn_settings} --global-settings %{_mvn_settings}"
elif [ -f %{_builddir}/.m2/settings.xml ] ; then
  echo "ok - picking up %{_builddir}/.m2/settings.xml"
  xml_setting_str="--settings %{_builddir}/.m2/settings.xml --global-settings %{_builddir}/.m2/settings.xml"
elif [ -f /etc/alti-maven-settings/settings.xml ] ; then
  echo "ok - applying local installed maven repo settings.xml for first priority"
  xml_setting_str="--settings /etc/alti-maven-settings/settings.xml --global-settings /etc/alti-maven-settings/settings.xml"
else
  echo "ok - applying default repository from pom.xml"
  xml_setting_str=""
fi

# TODO: This needs to align with Maven settings.xml, however, Maven looks for
# -SNAPSHOT in pom.xml to determine which repo to use. This creates a chain reaction on 
# legacy pom.xml design on other application since they are not implemented in the Maven way.
# :-( 
# Will need to create a work around with different repo URL and use profile Id to activate them accordingly
# mvn_release_flag=""
# if [ "x%{_production_release}" == "xtrue" ] ; then
#   mvn_release_flag="-Preleases"
# else
#   mvn_release_flag="-Psnapshots"
# fi

mvn_cmd="mvn -U -X $spark_profile_str $xml_setting_str package"
echo "$mvn_cmd"
$mvn_cmd
# You should expect livy-server-x.x.x-incubating.zip appears in assembly/target/ dir
# assembly name is livy-server defined in assembly/pom.xml and 
# version string x.x.x-incubating is 0.4.0-incubating defined in pom.xml

if [ $? -eq 0 ] ; then
  popd
  echo "ok - build livy project completed successfully!"
else
  popd
  echo "fail - build livy failed"
  exit -10
fi

%install
# manual cleanup for compatibility, and to be safe if the %clean isn't implemented
rm -rf %{buildroot}%{install_livy_dest}
# re-create installed dest folders
mkdir -p %{buildroot}%{install_livy_dest}
echo "compiled/built folder is (not the same as buildroot) RPM_BUILD_DIR = %{_builddir}"
echo "test installtion folder (aka buildroot) is RPM_BUILD_ROOT = %{buildroot}"
echo "test install livy dest = %{buildroot}/%{install_livy_dest}"
echo "test install livy label livy_folder_name = %{livy_folder_name}"
%{__mkdir} -p %{buildroot}%{install_livy_dest}/
%{__mkdir} -p %{buildroot}%{install_livy_dest}/tmp

cp -rp %{_builddir}/%{build_service_name}/assembly/target/livy-server-%{_livy_version}-incubating.zip %{buildroot}%{install_livy_dest}/tmp
pushd %{buildroot}%{install_livy_dest}/tmp
unzip livy-server-%{_livy_version}-incubating.zip
pushd livy-server-%{_livy_version}-incubating
mv * %{buildroot}%{install_livy_dest}/
popd
popd

# clean up
rm -rf %{buildroot}%{install_livy_dest}/tmp
touch %{buildroot}/%{install_livy_label}
echo "name=%{name}" >> %{buildroot}/%{install_livy_label}
echo "version=%{_livy_version}" >> %{buildroot}/%{install_livy_label}
echo "release=%{name}-%{release}" >> %{buildroot}/%{install_livy_label}
echo "git_rev=%{_git_hash_release}" >> %{buildroot}/%{install_livy_label}

%clean
echo "ok - cleaning up temporary files, deleting %{buildroot}%{install_livy_dest}"
rm -rf %{buildroot}%{install_livy_dest}

%files
%defattr(0644,root,root,0644)
%{install_livy_dest}/bin
%attr(0755,root,root) %{install_livy_dest}/bin/livy-server
%{install_livy_dest}/rsc-jars
%{install_livy_dest}/repl_2.11-jars
%{install_livy_dest}/repl_2.10-jars
%{install_livy_dest}/jars
%doc %{install_livy_label}
%doc %{install_livy_dest}/LICENSE
%doc %{install_livy_dest}/THIRD-PARTY
%doc %{install_livy_dest}/NOTICE
%doc %{install_livy_dest}/DISCLAIMER
%attr(0644,root,root) %{install_livy_conf}/*.template
%config %{install_livy_conf}

%post

%postun

%changelog
* Fri Feb 2 2018 Andrew Lee 20180202
- Initial Creation of spec file for Apache Livy 0.4.0
