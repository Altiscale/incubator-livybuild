#!/bin/bash -ex

# This legacy script to package RPM via FPM is wrong. We should stop doing this.
# Reinventing the wheel manually....

curr_dir=`dirname $0`
curr_dir=`cd $curr_dir; pwd`
rpm_file=""

if [ -f "$curr_dir/setup_env.sh" ]; then
  set -a
	source "$curr_dir/setup_env.sh"
  set +a
fi

ALTISCALE_RELEASE=${ALTISCALE_RELEASE:-4.0.0}
RPM_DESCRIPTION="Apache Livy ${LIVY_VERSION}\n\n${DESCRIPTION}"

# convert the tarball into an RPM
#create the installation directory (to stage artifacts)
mkdir -p --mode 0755 ${INSTALL_DIR}

OPT_DIR=${INSTALL_DIR}/opt
mkdir --mode=0755 -p ${OPT_DIR}
cd ${OPT_DIR}

mv ${WORKSPACE}/alti-livy/assembly/target/livy-server-${LIVY_VERSION}-incubating.zip ${OPT_DIR}/
pushd ${OPT_DIR}
unzip livy-server-${LIVY_VERSION}-incubating.zip
mv livy-server-${LIVY_VERSION}-incubating livy-${LIVY_VERSION}
popd
chmod 755 ${OPT_DIR}/livy-${LIVY_VERSION}

cd ${INSTALL_DIR}

cd ${RPM_DIR}

export RPM_NAME=`echo alti-livy-${LIVY_VERSION}`
fpm --verbose \
--maintainer andrew.lee02@sap.com \
--vendor SAP \
--provides ${RPM_NAME} \
--url ${GITREPO} \
--license "Apache License v2" \
-s dir \
-t rpm \
-n ${RPM_NAME}  \
-v ${ALTISCALE_RELEASE} \
--iteration ${DATE_STRING} \
--description "${RPM_DESCRIPTION}" \
${CONFIG_FILES} \
--rpm-attr 755,root,root:/opt/livy/bin/livy-server \
-C ${INSTALL_DIR} \
opt


exit $?












