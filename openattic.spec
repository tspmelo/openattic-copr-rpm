#
# spec file for package openattic
#
# Copyright (c) 2016-2017 SUSE LINUX GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/

Name: openattic
Version: 3.6.1
Release: 0
Summary: Open Source Management and Monitoring System for Ceph
Group: System Environment/Libraries
License: GPL-2.0
URL: http://www.openattic.org
BuildArch: noarch
Source:	%{name}-%{version}.tar.bz2
BuildRequires: postgresql
BuildRequires: postgresql-server
BuildRequires: python
BuildRequires: rsync
# PreReq:        %fillup_prereq

%{?systemd_requires}
PreReq: epel-release
Requires: python
Requires: python-pip
Requires: python-django >= 1.6.11
Requires: mod_wsgi
Requires: dbus
Requires: postgresql-server
Requires: python-configobj
Requires: python-django-filter = 0.7
Requires: python-djangorestframework >= 2.4.4
Requires: python-djangorestframework-bulk
Requires: pygobject2
Requires: python-pam
Requires: python-psycopg2
Requires: python-requests
Requires: ceph-common >= 12.2.0
Requires: postgresql
Requires: python-requests-aws
Requires(pre): shadow-utils

# These subpackages have been removed in 2.0.19 (OP#1968)
Obsoletes: %{name}-module-ipmi <= 2.0.18
Obsoletes: %{name}-module-mdraid <= 2.0.18
Obsoletes: %{name}-module-twraid <= 2.0.18

# These subpackages have been removed in 3.0.0 (OP#2127)
Obsoletes: %{name}-module-btrfs <= 3.0.0
Obsoletes: %{name}-module-cron <= 3.0.0
Obsoletes: %{name}-module-drbd <= 3.0.0
Obsoletes: %{name}-module-http <= 3.0.0
Obsoletes: %{name}-module-lio <= 3.0.0
Obsoletes: %{name}-module-lvm <= 3.0.0
Obsoletes: %{name}-module-mailaliases <= 3.0.0
Obsoletes: %{name}-module-nfs <= 3.0.0
Obsoletes: %{name}-module-samba <= 3.0.0
Obsoletes: %{name}-module-volumes <= 3.0.0
Obsoletes: %{name}-module-zfs <= 3.0.0

# These subpackages have merged into the main "openattic" package in 3.1.2
# (OP#2342)
Obsoletes: %{name}-base <= 3.1.2
Obsoletes: %{name}-gui <= 3.1.2
Obsoletes: %{name}-module-ceph <= 3.1.2
Obsoletes: %{name}-module-ceph-deployment <= 3.1.2
Obsoletes: %{name}-module-icinga <= 3.1.2
Obsoletes: %{name}-pgsql <= 3.1.2
Provides: %{name}-base
Provides: %{name}-gui
Provides: %{name}-module-ceph
Provides: %{name}-module-ceph-deployment
Provides: %{name}-module-icinga
Provides: %{name}-pgsql

# OpenATTIC and Crowbar's apache configurations conflict with each other,
# and in any case we (SUSE) don't support installing openATTIC on a Crowbar
# admin node.
Conflicts:  crowbar

%description
openATTIC is an Open Source Management and Monitoring System for the Ceph
distributed storage system <http://ceph.com>.

Various resources of a Ceph cluster can be managed and monitored via a web-based
management interface. It is no longer necessary to be intimately familiar with
the inner workings of the individual Ceph components.

Any task can be carried out by either using openATTIC’s clean and intuitive web
interface or via the openATTIC REST API.

openATTIC itself is stateless - it remains in a consistent state even if you
make changes to the Ceph cluster's resources using external command-line tools.

Upstream URL: http://www.openattic.org

%prep
%setup -q

%build

%install

# Build up target directory structure
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/openattic-gui
mkdir -p %{buildroot}%{_localstatedir}/lib/%{name}/static
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}
mkdir -p %{buildroot}%{_localstatedir}/lock/%{name}
mkdir -p %{buildroot}%{_localstatedir}/www/html/
mkdir -p %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d/
mkdir -p %{buildroot}%{_sysconfdir}/cron.daily/
mkdir -p %{buildroot}%{_sysconfdir}/dbus-1/system.d/
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d/
mkdir -p %{buildroot}%{_sysconfdir}/default/
mkdir -p %{buildroot}%{_sysconfdir}/%{name}/
mkdir -p %{buildroot}/lib/systemd/system/
mkdir -p %{buildroot}/lib/tmpfiles.d/
#mkdir -p %{buildroot}%{_sysconfdir}/sysconfig

# Install Backend and binaries
rsync -aAX backend/ %{buildroot}%{_datadir}/%{name}
install -m 644 version.txt %{buildroot}%{_datadir}/%{name}
rm -f  %{buildroot}%{_datadir}/%{name}/.style.yapf
rm -f  %{buildroot}%{_datadir}/%{name}/.pep8
install -m 755 bin/oaconfig   %{buildroot}%{_sbindir}

# %py_byte_compile %{__python2} %{buildroot}%{_datadir}/%{name}
python -m compileall %{buildroot}%{_datadir}/%{name}

# Install Web UI
rsync -aAX webui/dist/ %{buildroot}%{_datadir}/openattic-gui/
sed -i -e 's/^ANGULAR_LOGIN.*$/ANGULAR_LOGIN = False/g' %{buildroot}%{_datadir}/%{name}/settings.py

# Install HTML redirect
install -m 644 webui/redirect.html %{buildroot}%{_localstatedir}/www/html/index.html

# Install /etc/default/openattic
# TODO: move file to /etc/sysconfig/openattic instead (requires fixing all scripts that source it)
install -m 644 rpm/sysconfig/%{name}.RedHat %{buildroot}/%{_sysconfdir}/default/%{name}

# Install db file
install -m 640 etc/openattic/database.ini %{buildroot}%{_sysconfdir}/%{name}/

# configure dbus
install -m 644 etc/dbus-1/system.d/openattic.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/

install -m 644 etc/logrotate.d/%{name} %{buildroot}%{_sysconfdir}/logrotate.d/
touch %{buildroot}%{_localstatedir}/log/%{name}/%{name}.log

# install man pages
install -m 644 man/*.1 %{buildroot}%{_mandir}/man1/
gzip %{buildroot}%{_mandir}/man1/*.1

install -m 444 etc/systemd/*.service %{buildroot}/lib/systemd/system/
install -m 644 etc/tmpfiles.d/%{name}.conf %{buildroot}/lib/tmpfiles.d/

# openATTIC httpd config
install -m 644 etc/apache2/conf-available/%{name}.conf         %{buildroot}%{_sysconfdir}/httpd/conf.d/

# Install daily cron job
install -m 755 etc/cron.daily/%{name} %{buildroot}%{_sysconfdir}/cron.daily/

# create openattic user/group  if it does not exist
%pre
if getent group openattic > /dev/null ; then
  echo "openattic group already exists"
else
  groupadd -r openattic
  groupmems -g openattic -a apache
fi

if getent passwd openattic > /dev/null ; then
  echo "openattic user already exists"
else
  useradd -r -g openattic -d /var/lib/openattic -s /bin/bash -c "openATTIC System User" openattic
  groupmems -g apache -a openattic
fi
exit 0

%post
systemctl daemon-reload
systemctl restart dbus
systemctl enable httpd
systemctl start httpd

systemctl enable postgresql
systemctl start postgresql

%posttrans
# The setup of apache2 may not be finished at the post stage due to
# scriptlets included in apache2's own posttrans. So we need to move
# the attempt to start it here:
oaconfig install
systemctl daemon-reload
systemctl restart dbus
systemctl enable httpd
systemctl start httpd

%postun
if [ $1 -eq 0 ] ; then
    echo "Note: removing this package does not delete the"
    echo "corresponding PostgreSQL database by default."
    echo "If you want to drop the openATTIC database and"
    echo "database user, run the following commands as root:"
    echo ""
    echo "su - postgres -c psql"
    echo "postgres=# drop database openattic;"
    echo "postgres=# drop user openattic;"
    echo "postgres=# \q"
    echo ""
fi

%files

%defattr(-,openattic,openattic,-)
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/log/%{name}
%attr(660,-,-) %{_localstatedir}/log/%{name}/%{name}.log
%dir %{_localstatedir}/lock/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/database.ini

%defattr(-,root,root,-)
%doc CHANGELOG CONTRIBUTING.rst COPYING README.rst
%doc %{_mandir}/man1/oaconfig.1.gz

%dir %{_sysconfdir}/%{name}/

%config %{_sysconfdir}/dbus-1/system.d/%{name}.conf
%config %{_sysconfdir}/httpd/conf.d/%{name}.conf
%config %{_sysconfdir}/logrotate.d/%{name}

%{_sysconfdir}/cron.daily/%{name}

# %config %{_sysconfdir}/sysconfig/openattic

%{_localstatedir}/www/html/index.html
%{_datadir}/%{name}
%{_datadir}/%{name}-gui
/lib/tmpfiles.d/%{name}.conf
%{_sbindir}/oaconfig
/lib/systemd/system/%{name}-systemd.service
%dir %{_sysconfdir}/%{name}
%config %{_sysconfdir}/default/%{name}

%changelog
